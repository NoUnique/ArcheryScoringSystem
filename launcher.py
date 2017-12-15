from common import ui, common
from archery import archery
from tkinter import filedialog
from os import path, listdir, mkdir
from PIL import Image, ImageTk, ImageDraw
from random import randrange
import numpy
import sympy
import serial
import time

DEFAULT_DIR = "./data"
SAVE_DIR = "./patches"
CONFIG_FILE = "config.txt"
SERIAL_EOL = b'\n'

CANVAS_SIZE = 600 # pixels
BOARD_SIZE = 800 # mm
SENSOR_POSITION = BOARD_SIZE / 2 # mm
SPEED = 50 * 1000 # mm/s
TIME_INTERVAL = 7 # seconds

dist = numpy.linalg.norm

class Launcher(ui.AppFrame):
    # Initialize
    def __init__(self, xml):
        super().__init__(xml)
        self.set_title("LetGo Auto Scoring Board")
        self.state = ui.Tk.IntVar()
        self.state.trace('w', self.change_state)
        self.state.set(1)
        self._init_labels()
        self._init_entries()
        archery.DIM = CANVAS_SIZE
        archery.draw_scoreboard(self.find("cvScoreBoard"))
        self.find("cvScoreBoard").config(width=CANVAS_SIZE, height=CANVAS_SIZE)
        self.elements["cvScoreBoard"].bind("<Button-1>", self._set_impact)
        self.sensors = []
        self.text = {}
        self.detect_time = 0
        self._init_sensors()
        self._init_serial()

    def run(self):
        while (self.flag_terminate is not True):
            #self.update_idletasks()
            common.delay()
            if time.time() > self.detect_time + TIME_INTERVAL:
                try:
                    self._read_sensors()
                except Exception as e:
                    print("Error: Unable to read a sensor")
                    print(e)
                # predict when all sensors are read
                check = True
                for sensor in self.sensors:
                    if sensor.time <= 0.0:
                        check = False
                if check == True:
                    try:
                        self._predict()
                    except Exception as p:
                        print("Error: Unable to predict")
                        print(p)
                    for sensor in self.sensors:
                        sensor.time = 0
                    self.detect_time = time.time()

            # update display
            self.update()

    def _read_sensors(self):
        while True:
            c = self.serial.read(1)
            if c:
                if c == SERIAL_EOL:
                    self.buffer_end = True
                    break
                elif c == b'\r':
                    pass
                else:
                    self.buffer += c
            else:
                break
        if self.buffer_end:
            data = self.buffer.decode('utf-8').split('@')
            print(data)
            for i in range(4):
                if(i == 0):
                    offset = 1000
                elif(i == 1):
                    offset = 0
                elif(i == 2):
                    offset = 0
                else:
                    offset = 0

                self.sensors[i].time = (float(data[i]) + offset)\
                                        / 1000000.0 # micro second
                self._print_time(self.sensors[i])

            self.buffer = b''
            self.buffer_end = False

    class Sensor():
        def __init__(self, name, pos):
            self.name = name
            self.pos = pos
            self.time = 0.0
            print(self.pos)

    def _delete_point(self, name):
        canvas = self.find("cvScoreBoard")
        if(name in self.elements):
            canvas.delete(self.elements[name])

    def _draw_point(self, name, pos, r=5, color='green'):
        canvas = self.find("cvScoreBoard")
        point = canvas.create_oval(pos[0]-r/2+1, pos[1]-r/2+1, pos[0]+r/2+1, pos[1]+r/2+1,
                                   fill=color)
        self._delete_point(name)
        self.elements[name] = point

    def change_state(self, *args):
        self.set("lbState", "Shot " + str(self.state.get()))

    def _init_labels(self):
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

    def _init_entries(self):
        self.set("enNWx", -SENSOR_POSITION)
        self.set("enNWy", -SENSOR_POSITION)
        self.set("enNEx", SENSOR_POSITION)
        self.set("enNEy", -SENSOR_POSITION)
        self.set("enSWx", -SENSOR_POSITION)
        self.set("enSWy", SENSOR_POSITION)
        self.set("enSEx", SENSOR_POSITION)
        self.set("enSEy", SENSOR_POSITION)
        for i in range(10):
            var = self.variables["enShot"+str(i+1)]
            var.trace('w', self._calculate_total)

    def _init_sensors(self):
        for dir in ['NW', 'NE', 'SW', 'SE']:
            arcpos = numpy.array( (float(self.get("en"+dir+"x")), float(self.get("en"+dir+"y"))) )
            pos = arcpos2pos(arcpos)
            self._draw_point('sensor'+dir, pos, r=10, color='red')
            self.sensors.append(self.Sensor(dir, arcpos))

    def _init_serial(self):
        self.serial = serial.Serial(port='COM4',
                                    baudrate=9600,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    bytesize=serial.EIGHTBITS,
                                    timeout=0)
        self.buffer = b''
        self.buffer_end = False

    def _print_time(self, sensor):
        canvas = self.find("cvScoreBoard")
        pos = arcpos2pos(sensor.pos) + 1 # canvas point offset
        timetext = canvas.create_text(pos[0], pos[1],
                                      fill="green",
                                      anchor=sensor.name.lower(),
                                      text='{0:.8f}'.format(round(sensor.time, 8)))
        if(sensor.name in self.text):
            canvas.delete(self.text[sensor.name])
        self.text[sensor.name] = timetext

    def _set_impact(self, event):
        pos = numpy.array( (event.x, event.y) ) - 1 # canvas point offset
        arcpos = pos2arcpos(pos)
        self.point = numpy.array(arcpos)
        point = self._draw_point('impact', pos, r=5, color='green')
        print(self.point)
        for sensor in self.sensors:
            #print(sensor.pos)
            #print(self.point)
            rand = randrange(970, 1060)/1000.0
            #rand = 1
            sensor.time = numpy.linalg.norm(sensor.pos - self.point)\
                          /(SPEED * rand)
            self._print_time(sensor)

    def _reset_scores(self):
        # delete points in canvases
        self._delete_point('impact')
        self._delete_point('AVG')
        for i in range(12):
            self._delete_point('P'+str(i))
        # delete number in entries
        for i in range(10):
            self.set("enShot"+str(i+1), "")
        self.state.set(1)

    def _predict(self):
        x,y = sympy.symbols('x y', real=True)
        sqrt = sympy.sqrt
        solve = sympy.nsolve # numerial solver of sympy

        x1, y1 = self.sensors[0].pos # NW
        x2, y2 = self.sensors[1].pos # NE
        x3, y3 = self.sensors[2].pos # SW
        x4, y4 = self.sensors[3].pos # SE
        t12 = self.sensors[0].time - self.sensors[1].time # NW-NE
        t13 = self.sensors[0].time - self.sensors[2].time # NW-SW
        t14 = self.sensors[0].time - self.sensors[3].time # NW-SE
        t23 = self.sensors[1].time - self.sensors[2].time # NE-SW
        t24 = self.sensors[1].time - self.sensors[3].time # NE-SE
        t34 = self.sensors[2].time - self.sensors[3].time # SW-SE

        H12 = sqrt( (x-x1)**2+(y-y1)**2 ) - sqrt( (x-x2)**2+(y-y2)**2 ) - SPEED*t12
        H13 = sqrt( (x-x1)**2+(y-y1)**2 ) - sqrt( (x-x3)**2+(y-y3)**2 ) - SPEED*t13
        H14 = sqrt( (x-x1)**2+(y-y1)**2 ) - sqrt( (x-x4)**2+(y-y4)**2 ) - SPEED*t14
        H23 = sqrt( (x-x2)**2+(y-y2)**2 ) - sqrt( (x-x3)**2+(y-y3)**2 ) - SPEED*t23
        H24 = sqrt( (x-x2)**2+(y-y2)**2 ) - sqrt( (x-x4)**2+(y-y4)**2 ) - SPEED*t24
        H34 = sqrt( (x-x3)**2+(y-y3)**2 ) - sqrt( (x-x4)**2+(y-y4)**2 ) - SPEED*t34
        hyperbolas = [H12, H13, H14, H23, H24, H34]
        points = []
        for i in range(3, 49): # from 3(b000011) to 48(b110000)
            selection = bin(i)[2:].zfill(6)
            if (selection.count('1') != 2):
                continue # don't calculate if 2 hyperbolas are selected
            if (selection in ['100001', '010010', '001100']):
                continue # cases of no intersection
            #print(selection)
            i1 = selection.index('1')
            i2 = selection[i1+1:].zfill(6).index('1')
            vector = (1,1)
            intersection = solve( (hyperbolas[i1],hyperbolas[i2]), (x,y), vector )
            point = numpy.array( (intersection[0], intersection[1]) )
            points.append(point)
            #print(point)

        for i in range(len(points)):
            p = points[i]
            pos = arcpos2pos(p)
            self._draw_point('P'+str(i), pos, r=5, color='orange')
        AVG = numpy.array( (sum([p[0] for p in points])/len(points),
                            sum([p[1] for p in points])/len(points)) )
        posAVG = arcpos2pos(AVG)
        self._draw_point('AVG', posAVG, r=5, color='red')

        # predict score
        score = archery.estimate_score(AVG)
        self.set("enShot"+str(self.state.get()), str(score))
        if(self.state.get() < 10):
            self.state.set(self.state.get() + 1)
        else:
            # Total Score Pop-up
            total_score = self.get("enTotal")
            ui.Tk.messagebox.showinfo("Result of 10 Shots",
                                      "Total Score : " + total_score)
            self._reset_scores()

    def _calculate_total(self, *args):
        sum = 0
        for i in range(10):
            score = self.get("enShot"+str(i+1))
            if (score.isdigit()):
                sum += int(score)
        self.set("enTotal", sum)

    def btnReset_Click(self):
        self._reset_scores()

    def btnSimulate_Click(self):
        self._predict()

    def btnSet_Click(self):
        self._init_sensors()

    def btnModify_Click(self):
        pos = self.point / BOARD_SIZE * archery.DIA
        score = archery.estimate_score(pos)
        self.set("enShot"+str(self.state.get()-1), str(score))

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
