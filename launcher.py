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
            #rand = 1
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
        solve = sympy.nsolve
        t12 = self.sensors[0].time - self.sensors[1].time # NW-NE
        t13 = self.sensors[0].time - self.sensors[2].time # NW-SW
        t14 = self.sensors[0].time - self.sensors[3].time # NW-SE
        t24 = self.sensors[1].time - self.sensors[3].time # NE-SE
        t34 = self.sensors[2].time - self.sensors[3].time # SW-SE

        x1, y1 = self.sensors[0].pos
        x2, y2 = self.sensors[1].pos
        x3, y3 = self.sensors[2].pos
        x4, y4 = self.sensors[3].pos
        H12_H13 = solve((sqrt((x-x1)**2+(y-y1)**2)-sqrt((x-x2)**2+(y-y2)**2)-SPEED*t12,
                         sqrt((x-x1)**2+(y-y1)**2)-sqrt((x-x3)**2+(y-y3)**2)-SPEED*t13),
                         (x, y), (-1, -1))
        H12_H14 = solve((sqrt((x-x1)**2+(y-y1)**2)-sqrt((x-x2)**2+(y-y2)**2)-SPEED*t12,
                         sqrt((x-x1)**2+(y-y1)**2)-sqrt((x-x4)**2+(y-y4)**2)-SPEED*t14),
                         (x, y), (-1, 1))
        H13_H14 = solve((sqrt((x-x1)**2+(y-y1)**2)-sqrt((x-x3)**2+(y-y3)**2)-SPEED*t13,
                         sqrt((x-x1)**2+(y-y1)**2)-sqrt((x-x4)**2+(y-y4)**2)-SPEED*t14),
                         (x, y), (1, 1))
        P23 = numpy.array((H12_H13[0], H12_H13[1]))
        P24 = numpy.array((H12_H14[0], H12_H14[1]))
        P34 = numpy.array((H13_H14[0], H13_H14[1]))
        print(P23)
        print(P24)
        print(P34)
        points = []
        points.append(P23)
        points.append(P24)
        points.append(P34)
        AVG = numpy.array((sum([p[0] for p in points])/len(points),
                           sum([p[1] for p in points])/len(points)))
        posP23 = arcpos2pos(P23)
        posP24 = arcpos2pos(P24)
        posP34 = arcpos2pos(P34)
        posAVG = arcpos2pos(AVG)
        self._draw_point('P23', posP23, r=5, color='orange')
        self._draw_point('P24', posP24, r=5, color='orange')
        self._draw_point('P34', posP34, r=5, color='orange')
        self._draw_point('AVG', posAVG, r=5, color='red')

    def btnClose_Click(self):
        self.flag_terminate = True
        return

def arcpos2pos(arcpos):
    return (arcpos + BOARD_SIZE/2) / BOARD_SIZE * CANVAS_SIZE

def pos2arcpos(pos):
    return pos / CANVAS_SIZE * BOARD_SIZE - BOARD_SIZE/2

if __name__ == '__main__':
    # Load UI Layout
    app = Launcher('layout.xml')
    app.run()
