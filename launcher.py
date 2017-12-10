from common import ui, common
from archery import archery
from tkinter import filedialog
from os import path, listdir, mkdir
from PIL import Image, ImageTk, ImageDraw
from random import randrange
import numpy
import sympy

DEFAULT_DIR = "./data"
SAVE_DIR = "./patches"
CONFIG_FILE = "config.txt"

SENSOR_POSITION = 400 # mm
CANVAS_SIZE = 400 # pixels
BOARD_SIZE = 800 # mm
SPEED = 3000 * 1000 # mm/s

dist = numpy.linalg.norm

class Launcher(ui.AppFrame):
    # Initialize
    def __init__(self, xml):
        super().__init__(xml)
        self.set_title("LetGo Auto Scoring Board")
        self.set("lbNWx", "mm")
        self.set("lbNWy", "mm")
        self.set("lbNEx", "mm")
        self.set("lbNEy", "mm")
        self.set("lbSWx", "mm")
        self.set("lbSWy", "mm")
        self.set("lbSEx", "mm")
        self.set("lbSEy", "mm")
        self.set("lbShot1", "Shot1")
        self.set("lbShot2", "Shot2")
        self.set("lbShot3", "Shot3")
        self.set("lbShot4", "Shot4")
        self.set("lbShot5", "Shot5")
        self.set("lbShot6", "Shot6")
        self.set("lbShot7", "Shot7")
        self.set("lbShot8", "Shot8")
        self.set("lbShot9", "Shot9")
        self.set("lbShot10", "Shot10")
        self.set("lbTotal", "Total")
        self.set("enNWx", -SENSOR_POSITION)
        self.set("enNWy", -SENSOR_POSITION)
        self.set("enNEx", SENSOR_POSITION)
        self.set("enNEy", -SENSOR_POSITION)
        self.set("enSWx", -SENSOR_POSITION)
        self.set("enSWy", SENSOR_POSITION)
        self.set("enSEx", SENSOR_POSITION)
        self.set("enSEy", SENSOR_POSITION)
        archery.DIM = CANVAS_SIZE
        archery.draw_scoreboard(self.find("cvScoreBoard"))
        self.find("cvScoreBoard").config(width=CANVAS_SIZE, height=CANVAS_SIZE)
        self.elements["cvScoreBoard"].bind("<Button-1>", self._set_impact)
        self.sensors = []
        self.text = {}
        self._init_sensors()

    def run(self):
        while (self.flag_terminate is not True):
            #self.update_idletasks()
            common.delay()
            self.update()

    class Sensor():
        def __init__(self, name, pos):
            self.name = name
            self.pos = pos
            self.time = 0.0
            print(self.pos)

    def _draw_point(self, name, pos, r=5, color='green'):
        canvas = self.find("cvScoreBoard")
        point = canvas.create_oval(pos[0]-r/2+1, pos[1]-r/2+1, pos[0]+r/2+1, pos[1]+r/2+1,
                                   fill=color)
        if(name in self.elements):
            canvas.delete(self.elements[name])
            pass
        self.elements[name] = point

    def _init_sensors(self):
        for dir in ['NW', 'NE', 'SW', 'SE']:
            arcpos = numpy.array((float(self.get("en"+dir+"x")), float(self.get("en"+dir+"y"))))
            pos = arcpos2pos(arcpos)
            self._draw_point('sensor'+dir, pos, r=10, color='red')
            self.sensors.append(self.Sensor(dir, arcpos))

    def _set_impact(self, event):
        pos = numpy.array((event.x, event.y)) - 1 # canvas point offset
        arcpos = pos2arcpos(pos)
        self.point = numpy.array(arcpos)
        point = self._draw_point('impact', pos, r=5, color='green')
        print(self.point)
        for sensor in self.sensors:
            #print(sensor.pos)
            #print(self.point)
            arrivetime = numpy.linalg.norm(sensor.pos - self.point) / SPEED
            rand = randrange(970, 1060)/1000.0
            rand = 1
            sensor.time = arrivetime * rand

            canvas = self.find("cvScoreBoard")
            pos = arcpos2pos(sensor.pos) + 1 # canvas point offset
            timetext = canvas.create_text(pos[0], pos[1],
                                          fill="green",
                                          anchor=sensor.name.lower(),
                                          text='{0:.8f}'.format(round(sensor.time, 8)))
            if(sensor.name in self.text):
                canvas.delete(self.text[sensor.name])
            self.text[sensor.name] = timetext


    def btnSet_Click(self):
        self._init_sensors()

    def btnSimulate_Click(self):
        x,y = sympy.symbols('x y', real=True)
        sqrt = sympy.sqrt
        solve = sympy.solve
        t12 = self.sensors[0].time - self.sensors[1].time # NW-NE
        t13 = self.sensors[0].time - self.sensors[2].time # NW-SW
        t24 = self.sensors[1].time - self.sensors[3].time # NE-SE
        t34 = self.sensors[2].time - self.sensors[3].time # SW-SE

        C = SENSOR_POSITION
        A12 = (SPEED * t12) / 2
        B12 = sqrt(C**2 - A12**2)
        A13 = (SPEED * t13) / 2
        B13 = sqrt(C**2 - A13**2)
        A24 = (SPEED * t24) / 2
        B24 = sqrt(C**2 - A24**2)
        A34 = (SPEED * t34) / 2
        B34 = sqrt(C**2 - A34**2)
        H12_H13 = solve([(x/A12)**2-((y-C)/B12)**2-1, ((x-C)/B13)**2-(y/A13)**2+1], x, y)#[0]
        H12_H24 = solve([(x/A12)**2-((y-C)/B12)**2-1, ((x+C)/B24)**2-(y/A24)**2+1], x, y)#[0]
        H13_H34 = solve([((x-C)/B13)**2-(y/A13)**2+1, (x/A34)**2-((y+C)/B34)**2-1], x, y)#[0]
        H24_H34 = solve([((x+C)/B24)**2-(y/A24)**2+1, (x/A34)**2-((y+C)/B34)**2-1], x, y)#[0]
        print(sympy.simplify((x/A12)**2-((y-C)/B12)**2-1))
        print(sympy.simplify(((x-C)/B13)**2-(y/A13)**2+1))
        P213 = numpy.array(H12_H13)
        P124 = numpy.array(H12_H24)
        P134 = numpy.array(H13_H34)
        P243 = numpy.array(H24_H34)
        print(H12_H13)
        print(H12_H24)
        print(H13_H34)
        print(H24_H34)
        #print(P213)
        #print(P124)
        #print(P134)
        #print(P243)


        # Sum of squared distance
        #S = 

        # Impact Wave Propagation
        # young sik, Yoon's way : collect only 1/4 features(time differences)
        # 0 1 2 3
        # [If sensor0 is the fastest]
        # (0-1,
        #  0-2,
        #  0-3,
        #  1-2,
        #  1-3,
        #  2-3)
        # [If sensor1 is the fastest] (0-1, 2-3 switch)
        # (1-0,
        #  1-3,
        #  1-2,
        #  0-3,
        #  0-2,
        #  3-2)
        # [If sensor2 is the fastest] (2-0, 1-3 switch)
        # (2-3,
        #  2-0,
        #  2-1,
        #  3-0,
        #  3-1,
        #  0-1)
        # [If sensor3 is the fastest] (3-0, 1-2 switch)
        # (3-2,
        #  3-1,
        #  3-0,
        #  2-1,
        #  2-0,
        #  1-0)
        

    def btnClose_Click(self):
        self.flag_terminate = True
        return

def arcpos2pos(arcpos):
    #return tuple(map(lambda x:(x + BOARD_SIZE/2) / BOARD_SIZE * CANVAS_SIZE, arcpos))
    return (arcpos + BOARD_SIZE/2) / BOARD_SIZE * CANVAS_SIZE

def pos2arcpos(pos):
    #return tuple(map(lambda x:x / CANVAS_SIZE * BOARD_SIZE - archer.DIM/2, pos))
    return pos / CANVAS_SIZE * BOARD_SIZE - BOARD_SIZE/2

if __name__ == '__main__':
    # Load UI Layout
    app = Launcher('layout.xml')
    app.run()
