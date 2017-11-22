from common import ui, common
from archery import archery
from tkinter import filedialog
from os import path, listdir, mkdir
from PIL import Image, ImageTk, ImageDraw
import math

DEFAULT_DIR = "./data"
SAVE_DIR = "./patches"
CONFIG_FILE = "config.txt"

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
        self.set("enNWy", int(150/400*archery.DIM))
        self.set("enNEx", int(150/400*archery.DIM))
        self.set("enNEy", int(150/400*archery.DIM))
        self.set("enSWx", -int(150/400*archery.DIM))
        self.set("enSWy", -int(150/400*archery.DIM))
        self.set("enSEx", int(150/400*archery.DIM))
        self.set("enSEy", -int(150/400*archery.DIM))
        self.find("cvScoreBoard").config(width=archery.DIM, height=archery.DIM)
        archery.draw_scoreboard(self.find("cvScoreBoard"))

    def run(self):
        while (self.flag_terminate is not True):
            #self.update_idletasks()
            common.delay()
            self.update()

    class Sensor():
        def __init__(self, x, y):
            self.pos = (int(x), int(y))
            print(self.pos)

    def btnSet_Click(self):
        self.sensorNW = self.Sensor(self.get("enNWx"), self.get("enNWy"))
        self.sensorNE = self.Sensor(self.get("enNEx"), self.get("enNEy"))
        self.sensorSW = self.Sensor(self.get("enSWx"), self.get("enSWy"))
        self.sensorSE = self.Sensor(self.get("enSEx"), self.get("enSEy"))
        return

    def btnSimulate_Click(self):
        return

    def btnClose_Click(self):
        self.flag_terminate = True
        return


if __name__ == '__main__':
    # Load UI Layout
    app = Launcher('layout.xml')
    app.run()
