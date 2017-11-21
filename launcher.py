from common import ui, common
from wafer import generate
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
        self.set_title("Wafer Map Generator")
        self.config = {"curved" : {},
                       "straight" : {},
                       "defocus" : {},
                       "bull" : {},
                       "dounut" : {},
                       "edge" : {},
                       "random" : {}}
        self._load_config()

        # Initalize LabelFrame1 (Save Folder)
        self.set("lbSaveFolder", "Save Folder")
        self.set("lbGenerateNum", "Generate #")

        # Initalize LabelFrame2

        # Initalize DynamicLabelFrames
        self.count = {"curved" : 0,
                      "straight" : 0,
                      "defocus" : 0,
                      "bull" : 0,
                      "dounut" : 0,
                      "edge" : 0,
                      "random" : 0}
        # Initialize Layout
        for pattern in self.count.keys():
            self.elements["btn" + pattern.capitalize()].invoke()
        self.elements["btnRandom"].invoke()

    def run(self):
        while (self.flag_terminate is not True):
            #self.update_idletasks()
            common.delay()
            self.update()

    def _load_config(self):
        self.set("enSaveFolder", path.abspath(DEFAULT_DIR))
        self.curr_file = 1
        if(path.isfile(CONFIG_FILE)):
            with open(CONFIG_FILE, 'r') as f:
                conf = f.readlines()
                for i in range(len(conf)):
                    try:
                        att, val = [text.strip() for text in conf[i].split('=')]
                        pattern, attrib = [text.strip() for text in att.split('_')]
                        self.config[pattern][attrib] = int(val)
                    except:
                        ui.messagebox.showerror("Wrong Configuration", "[Line" + str(i+1) +"] Wrong Configuration. Check the 'config.txt' file")

    # Events
    def btnBrowse_Click(self):
        targetFolder = filedialog.askdirectory(initialdir=self.get("enSaveFolder"),
                                               title="Please select location of raw wafer images")
        if(targetFolder != ""):
            self.set("enSaveFolder", targetFolder)
            self._make_filelist()

    class Options(ui.Tk.LabelFrame):
        def __init__(self, master, pattern, **options):
            ui.Tk.LabelFrame.__init__(self, master.frame, **options)
            #ui.Tk.LabelFrame.__init__(self, master, **options)
            self.name = pattern
            self.count = master.count[pattern]
            self.master = master
            self.elements = {}
            self.variables = {}

            if(pattern=="curved"):
                # count : 곡선 개수
                self.variables["count-min"] = ui.Tk.IntVar()
                self.variables["count-max"] = ui.Tk.IntVar()
                self.elements["count-min"] = self.Scale("Count-Min", (0,0), (0,0))
                self.elements["count-max"] = self.Scale("Count-Max", (0,10), (0,1))
                # center : 중심이 위치할 원의 반지름
                self.variables["center-min"] = ui.Tk.IntVar()
                self.variables["center-max"] = ui.Tk.IntVar()
                self.elements["center-min"] = self.Scale("Center-Min", (0,0), (1,0))
                self.elements["center-max"] = self.Scale("Center-Max", (0,10), (1,1))
                # radius : curved 반지름
                self.variables["radius-min"] = ui.Tk.IntVar()
                self.variables["radius-max"] = ui.Tk.IntVar()
                self.elements["radius-min"] = self.Scale("Radius-Min", (0,0), (0,2))
                self.elements["radius-max"] = self.Scale("Radius-Max", (0,10), (0,3))
                # area radius : 출력 영역 반지름
                self.variables["arearad-min"] = ui.Tk.IntVar()
                self.variables["arearad-max"] = ui.Tk.IntVar()
                self.elements["arearad-min"] = self.Scale("AreaRad-Min", (0,0), (1,2))
                self.elements["arearad-max"] = self.Scale("AreaRad-Max", (0,10), (1,3))
                # weight : 굵기
                self.variables["weight-min"] = ui.Tk.IntVar()
                self.variables["weight-max"] = ui.Tk.IntVar()
                self.elements["weight-min"] = self.Scale("Weight-Min", (0,0), (0,4))
                self.elements["weight-max"] = self.Scale("Weight-Max", (0,10), (0,5))
                # smear : 내부 중심원의 위치 이동량(굵기의 변화를 주기 위함)
                self.variables["smear-min"] = ui.Tk.IntVar()
                self.variables["smear-max"] = ui.Tk.IntVar()
                self.elements["smear-min"] = self.Scale("Smear-Min", (0,0), (1,4))
                self.elements["smear-max"] = self.Scale("Smear-Max", (0,10), (1,5))
            elif(pattern=="straight"):
                # count : 직선 개수
                self.variables["count-min"] = ui.Tk.IntVar()
                self.variables["count-max"] = ui.Tk.IntVar()
                self.elements["count-min"] = self.Scale("Count-Min", (0,0), (0,0))
                self.elements["count-max"] = self.Scale("Count-Max", (0,10), (0,1))
                # length : 직선 길이
                self.variables["length-min"] = ui.Tk.IntVar()
                self.variables["length-max"] = ui.Tk.IntVar()
                self.elements["length-min"] = self.Scale("Length-Min", (0,0), (1,0))
                self.elements["length-max"] = self.Scale("Length-Max", (0,10), (1,1))
                # weight : 굵기
                self.variables["weight-min"] = ui.Tk.IntVar()
                self.variables["weight-max"] = ui.Tk.IntVar()
                self.elements["weight-min"] = self.Scale("Weight-Min", (0,0), (1,2))
                self.elements["weight-max"] = self.Scale("Weight-Max", (0,10), (1,3))
                # smear : 굵기가 변하는 정도
                self.variables["smear-min"] = ui.Tk.IntVar()
                self.variables["smear-max"] = ui.Tk.IntVar()
                self.elements["smear-min"] = self.Scale("Smear-Min", (0,0), (1,4))
                self.elements["smear-max"] = self.Scale("Smear-Max", (0,10), (1,5))
            elif(pattern=="defocus"):
                # count : 방사형 직선 개수
                self.variables["count-min"] = ui.Tk.IntVar()
                self.variables["count-max"] = ui.Tk.IntVar()
                self.elements["count-min"] = self.Scale("Count-Min", (0,0), (0,0))
                self.elements["count-max"] = self.Scale("Count-Max", (0,10), (0,1))
                # length : 직선 길이
                self.variables["length-min"] = ui.Tk.IntVar()
                self.variables["length-max"] = ui.Tk.IntVar()
                self.elements["length-min"] = self.Scale("Length-Min", (0,0), (1,0))
                self.elements["length-max"] = self.Scale("Length-Max", (0,10), (1,1))
                # start : 내경 반지름
                self.variables["start-min"] = ui.Tk.IntVar()
                self.variables["start-max"] = ui.Tk.IntVar()
                self.elements["start-min"] = self.Scale("Start-Min", (0,0), (0,2))
                self.elements["start-max"] = self.Scale("Start-Max", (0,10), (0,3))
                # end : 외경 반지름
                self.variables["end-min"] = ui.Tk.IntVar()
                self.variables["end-max"] = ui.Tk.IntVar()
                self.elements["end-min"] = self.Scale("End-Min", (0,0), (1,2))
                self.elements["end-max"] = self.Scale("End-Max", (0,10), (1,3))
                # weight : 굵기
                self.variables["weight-min"] = ui.Tk.IntVar()
                self.variables["weight-max"] = ui.Tk.IntVar()
                self.elements["weight-min"] = self.Scale("Weight-Min", (0,0), (0,4))
                self.elements["weight-max"] = self.Scale("Weight-Max", (0,10), (0,5))
                # smear : 굵기가 변하는 정도
                self.variables["smear-min"] = ui.Tk.IntVar()
                self.variables["smear-max"] = ui.Tk.IntVar()
                self.elements["smear-min"] = self.Scale("Smear-Min", (0,0), (1,4))
                self.elements["smear-max"] = self.Scale("Smear-Max", (0,10), (1,5))
            elif(pattern=="bull"):
                # random : 생성/비생성을 랜덤으로 정함
                self.variables["random"] = ui.Tk.BooleanVar()
                self.elements["random"] = self.Checkbutton("Random", (0, 0))
                # size : 크기
                self.variables["size-min"] = ui.Tk.IntVar()
                self.variables["size-max"] = ui.Tk.IntVar()
                self.elements["size-min"] = self.Scale("Size-Min", (0,0), (1,0))
                self.elements["size-max"] = self.Scale("Size-Max", (0,10), (1,1))
                # smear1 : 번지는 부분1
                self.variables["smear1-min"] = ui.Tk.IntVar()
                self.variables["smear1-max"] = ui.Tk.IntVar()
                self.elements["smear1-min"] = self.Scale("Smear1-Min", (0,0), (1,2))
                self.elements["smear1-max"] = self.Scale("Smear1-Max", (0,10), (1,3))
                # smear2 : 번지는 부분1
                self.variables["smear2-min"] = ui.Tk.IntVar()
                self.variables["smear2-max"] = ui.Tk.IntVar()
                self.elements["smear2-min"] = self.Scale("Smear2-Min", (0,0), (1,4))
                self.elements["smear2-max"] = self.Scale("Smear2-Max", (0,10), (1,5))
            elif(pattern=="dounut"):
                # random : 생성/비생성을 랜덤으로 정함
                self.variables["random"] = ui.Tk.BooleanVar()
                self.elements["random"] = self.Checkbutton("Random", (0, 0))
                # radius : dounut 반지름
                self.variables["radius-min"] = ui.Tk.IntVar()
                self.variables["radius-max"] = ui.Tk.IntVar()
                self.elements["radius-min"] = self.Scale("Radius-Min", (0,0), (0,2))
                self.elements["radius-max"] = self.Scale("Radius-Max", (0,10), (0,3))
                # shift : 중심이 축에서 벗어나는 정도
                self.variables["shift-min"] = ui.Tk.IntVar()
                self.variables["shift-max"] = ui.Tk.IntVar()
                self.elements["shift-min"] = self.Scale("Shift-Min", (0,0), (1,2))
                self.elements["shift-max"] = self.Scale("Shift-Max", (0,10), (1,3))
                # weight : 굵기
                self.variables["weight-min"] = ui.Tk.IntVar()
                self.variables["weight-max"] = ui.Tk.IntVar()
                self.elements["weight-min"] = self.Scale("Weight-Min", (0,0), (0,4))
                self.elements["weight-max"] = self.Scale("Weight-Max", (0,10), (0,5))
                # smear : 굵기가 변하는 정도
                self.variables["smear-min"] = ui.Tk.IntVar()
                self.variables["smear-max"] = ui.Tk.IntVar()
                self.elements["smear-min"] = self.Scale("Smear-Min", (0,0), (1,4))
                self.elements["smear-max"] = self.Scale("Smear-Max", (0,10), (1,5))
            elif(pattern=="edge"):
                # random : 생성/비생성을 랜덤으로 정함
                self.variables["random"] = ui.Tk.BooleanVar()
                self.elements["random"] = self.Checkbutton("Random", (0, 0))
                # deadzone :비활성구간 
                self.variables["deadzone-min"] = ui.Tk.IntVar()
                self.variables["deadzone-max"] = ui.Tk.IntVar()
                self.elements["deadzone-min"] = self.Scale("Deadzone-Min", (0,0), (1,2))
                self.elements["deadzone-max"] = self.Scale("Deadzone-Max", (0,10), (1,3))
                # intense : 세기 
                self.variables["intense-min"] = ui.Tk.IntVar()
                self.variables["intense-max"] = ui.Tk.IntVar()
                self.elements["intense-min"] = self.Scale("Intense-Min", (0,0), (1,4))
                self.elements["intense-max"] = self.Scale("Intense-Max", (0,10), (1,5))
            elif(pattern=="random"):
                # white : white 색상 노이즈를 색성할 경우
                self.variables["white"] = ui.Tk.BooleanVar()
                self.elements["white"] = self.Checkbutton("White", (0, 0))
                # deadzone :비활성구간 
                self.variables["deadzone-min"] = ui.Tk.IntVar()
                self.variables["deadzone-max"] = ui.Tk.IntVar()
                self.elements["deadzone-min"] = self.Scale("Deadzone-Min", (0,0), (1,2))
                self.elements["deadzone-max"] = self.Scale("Deadzone-Max", (0,10), (1,3))
                # intense : 세기 
                self.variables["intense-min"] = ui.Tk.IntVar()
                self.variables["intense-max"] = ui.Tk.IntVar()
                self.elements["intense-min"] = self.Scale("Intense-Min", (0,0), (1,4))
                self.elements["intense-max"] = self.Scale("Intense-Max", (0,10), (1,5))
           
            self.elements["btnReset"] = self.Button("Reset", self.destroy, (0,12))
            self.elements["btnDelete"] = self.Button("Delete", self.destroy, (1,12))
            self.set_init(pattern)
            self.set_config()
            master.count[pattern] += 1

        def Button(self, title, function, grid):
            return ui.Tk.Button(self, text=title, width=11, command=function).grid(row=grid[0], column=grid[1], sticky=ui.Tk.constants.W)
        def Label(self, title, grid):
            return ui.Tk.Label(self, text=title, width=5).grid(row=grid[0], column=grid[1], sticky=ui.Tk.constants.W)
        def Checkbutton(self, title, grid):
            return ui.Tk.Checkbutton(self, text=title, width=11, variable=self.variables[title.lower()], anchor=ui.Tk.constants.CENTER, indicatoron=0).grid(row=grid[0], column=grid[1], sticky=ui.Tk.constants.W)

        def update_value(self, event):
            w = event.widget
            name = w.cget("label").lower()
            if(name.split('-')[1] == "max"):
                self.elements[name.split('-')[0]+'-min'].config(to=self.variables[name].get())
            else:
                self.elements[name.split('-')[0]+'-max'].config(from_=self.variables[name].get())
        def Scale(self, title, range, grid):
            temp = ui.Tk.Scale(self, label=title, from_=range[0], to=range[1], orient=ui.Tk.constants.HORIZONTAL, width=11, variable=self.variables[title.lower()])
            temp.grid(row=grid[0], column=grid[1], sticky=ui.Tk.constants.W)
            temp.bind("<ButtonRelease-1>", self.update_value)
            return temp

        def set_init(self, pattern):
            row_base = 0
            col_base = 0
            if(pattern=="curved"):
                self.config(text="Curved-Line "+str(self.count+1))
                row_base=10
            elif(pattern=="straight"):
                self.config(text="Straight-Line "+str(self.count+1))
                row_base=11
            elif(pattern=="defocus"):
                self.config(text="Defocus "+str(self.count+1))
                row_base=12
            elif(pattern=="bull"):
                self.config(text="Bull's Eye "+str(self.count+1))
                row_base=13
            elif(pattern=="dounut"):
                self.config(text="Dounut "+str(self.count+1))
                row_base=14
            elif(pattern=="edge"):
                self.config(text="Edge "+str(self.count+1))
                row_base=10
                col_base=10
            elif(pattern=="random"):
                self.config(text="Random Noise "+str(self.count+1))
                row_base=12
                col_base=10
            self.grid(row=row_base+self.count, column=col_base, columnspan=6, padx=2, pady=2)

        def set_config(self):
            pattern = self.name
            config = self.master.config[pattern]
            for attrib in config.keys():
                self.variables[attrib].set(config[attrib])

        def reset(self):
            pass

        def destroy(self):
            self.master.count[self.name] -= 1
            if(self.name in ["curved", "straight", "defocus", "bull", "dounut"]):
                self.master.set("btn" + self.name.capitalize(), False)
            ui.Tk.LabelFrame.destroy(self)
            for i in range(self.count+1, self.master.count[self.name]+1):
                self.master.elements[self.name+str(i+1)].count -= 1
                self.master.elements[self.name+str(i+1)].set_init(self.name)
                self.master.elements[self.name+str(i)] = self.master.elements[self.name+str(i+1)]
                del self.master.elements[self.name+str(i+1)]

def add_element(self, pattern):
        if((pattern in ["curved", "straight", "defocus", "bull", "dounut"]) and (self.count[pattern] > 0)):
            self.elements[pattern + str(self.count[pattern])].destroy()
        elif((pattern is "edge") and (self.count[pattern] > 1)):
            self.elements[pattern + str(self.count[pattern])].destroy()
        elif((pattern is "random") and (self.count[pattern] > 2)):
            self.elements[pattern + str(self.count[pattern])].destroy()
        else:
            self.elements[pattern + str(self.count[pattern])] = self.Options(self, pattern)

    def btnCurved_Click(self):
        self.add_element("curved")
    def btnStraight_Click(self):
        self.add_element("straight")
    def btnDefocus_Click(self):
        self.add_element("defocus")
    def btnBull_Click(self):
        self.add_element("bull")
    def btnDounut_Click(self):
        self.add_element("dounut")
    def btnEdge_Click(self):
        self.add_element("edge")
    def btnRandom_Click(self):
        self.add_element("random")

    def btnGenerate_Click(self):
        return

    def btnClose_Click(self):
        self.flag_terminate = True
        return


if __name__ == '__main__':
    # Load UI Layout
    app = Launcher('layout.xml')
    app.run()
