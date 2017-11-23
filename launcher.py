from common import ui, common
from archery import archery
from tkinter import filedialog
from os import path, listdir, mkdir
from PIL import Image, ImageTk, ImageDraw
from random import randrange
import numpy

DEFAULT_DIR = "./data"
SAVE_DIR = "./patches"
CONFIG_FILE = "config.txt"

SPEED = 3000 * 100 # mm/s

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
        self.set("enNWx", -int(150/400*archery.DIM))
        self.set("enNWy", -int(150/400*archery.DIM))
        self.set("enNEx", int(150/400*archery.DIM))
        self.set("enNEy", -int(150/400*archery.DIM))
        self.set("enSWx", -int(150/400*archery.DIM))
        self.set("enSWy", int(150/400*archery.DIM))
        self.set("enSEx", int(150/400*archery.DIM))
        self.set("enSEy", int(150/400*archery.DIM))
        self.find("cvScoreBoard").config(width=archery.DIM, height=archery.DIM)
        self.elements["cvScoreBoard"].bind("<Button-1>", self._set_impact)
        # archery.draw_scoreboard(self.find("cvScoreBoard"))
        self._init_sensors()

    def run(self):
        while (self.flag_terminate is not True):
            #self.update_idletasks()
            common.delay()
            self.update()

    class Sensor():
        def __init__(self, x, y):
            self.pos = numpy.array((int(x), int(y)))
            self.time = 0.0
            print(self.pos)

    def _init_sensors(self):
        sensorNW = self.Sensor(self.get("enNWx"), self.get("enNWy"))
        sensorNE = self.Sensor(self.get("enNEx"), self.get("enNEy"))
        sensorSW = self.Sensor(self.get("enSWx"), self.get("enSWy"))
        sensorSE = self.Sensor(self.get("enSEx"), self.get("enSEy"))
        self.sensors = [sensorNW, sensorNE, sensorSW, sensorSE]

    def _set_impact(self, event):
        self.point = numpy.array((event.x-1-archery.DIM/2, event.y-1-archery.DIM/2))
        print(self.point)

    def btnSet_Click(self):
        self._init_sensors()


    def btnSimulate_Click(self):
        # Impact Wave Propagation
        for sensor in self.sensors:
            distance = numpy.linalg.norm(sensor.pos, self.point) / SPEED
            rand = randrange(970, 1060)/1000.0
            sensor.time = distance * rand

            canvas = self.get("cvScoreBoard")
            canvas.create_text(sensor.x+1, sensor.y+1, fill="darkblue",
                               font="Times 20 italic bold",
                               text=str(round(sensor.time, 6)))

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


if __name__ == '__main__':
    # Load UI Layout
    app = Launcher('layout.xml')
    app.run()
