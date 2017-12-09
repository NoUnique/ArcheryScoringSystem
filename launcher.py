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

INITIAL_SENSOR_POSITION = 400 # mm
CANVAS_SIZE = 600 # pixels
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
        self.set("enNWx", -INITIAL_SENSOR_POSITION)
        self.set("enNWy", -INITIAL_SENSOR_POSITION)
        self.set("enNEx", INITIAL_SENSOR_POSITION)
        self.set("enNEy", -INITIAL_SENSOR_POSITION)
        self.set("enSWx", -INITIAL_SENSOR_POSITION)
        self.set("enSWy", INITIAL_SENSOR_POSITION)
        self.set("enSEx", INITIAL_SENSOR_POSITION)
        self.set("enSEy", INITIAL_SENSOR_POSITION)
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
            self.pos = numpy.array(pos)
            self.time = 0.0
            print(self.pos)

    def _init_sensors(self):
        for dir in ['NW', 'NE', 'SW', 'SE']:
            arcpos = (float(self.get("en"+dir+"x")), float(self.get("en"+dir+"y")))
            self.sensors.append(self.Sensor(dir, arcpos))

    def _draw_point(self, name, pos, r=5, color='green'):
        canvas = self.find("cvScoreBoard")
        if(name in self.elements):
            canvas.delete(self.elements[name])
        point = canvas.create_oval(pos[0]-r/2, pos[1]-r/2, pos[0]+r/2, pos[1]+r/2,
                                   fill=color)
        self.elements[name] = point

    def _set_impact(self, event):
        pos = numpy.array((event.x, event.y)) - 1 # canvas point offset
        arcpos = pos2arcpos(pos)
        self.point = numpy.array(arcpos)
        point = self._draw_point('impact', pos+1, r=5, color='green')
        print(self.point)
        for sensor in self.sensors:
            #print(sensor.pos)
            #print(self.point)
            arrivetime = numpy.linalg.norm(sensor.pos - self.point) / SPEED
            rand = randrange(970, 1060)/1000.0
            #rand = 1
            sensor.time = arrivetime * rand

            canvas = self.find("cvScoreBoard")
            pos = arcpos2pos(sensor.pos) + 1 # canvas point offset
            if(sensor.name in self.text):
                canvas.delete(self.text[sensor.name])
            timetext = canvas.create_text(pos[0], pos[1],
                                          fill="green",
                                          anchor=sensor.name.lower(),
                                          text='{0:.8f}'.format(round(sensor.time, 8)))
            self.text[sensor.name] = timetext


    def btnSet_Click(self):
        self._init_sensors()

    def btnSimulate_Click(self):
        x,y = sympy.symbols('x y')
        for sensor in self.sensors:
            sol = sympy.solve([sqrt((x-x1)**2+(y-y1)**2)-sqrt((x-x2)**2+(y-y2)**2)-t*SPEED,
                               sqrt((x-x1)**2+(y-y1)**2)-sqrt((x-x3)**2+(y-y3)**2)-t*SPEED],
                               [x,y]).values()
            p1 = numpy.array(list(sol))

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
