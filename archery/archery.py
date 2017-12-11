import types
from math import sqrt

DIM = 400 # pixels
DIA = 800 # mm

def _draw_circle(self, r, **kwargs):
    r = r / DIA * DIM
    if "width" in kwargs.keys():
        w = kwargs["width"] / DIA * DIM
        del kwargs["width"]
        return self.create_oval(DIM/2-r+1, DIM/2-r+1, DIM/2+r+1, DIM/2+r+1, width=w, **kwargs)
    else:
        return self.create_oval(DIM/2-r+1, DIM/2-r+1, DIM/2+r+1, DIM/2+r+1, **kwargs)

def _draw_horizon(self, l, **kwargs):
    l = l / DIA * DIM
    if "width" in kwargs.keys():
        w = kwargs["width"] / DIA * DIM
        del kwargs["width"]
        return self.create_line(DIM/2-l+1, DIM/2+1, DIM/2+l+1, DIM/2+1, width=w, **kwargs)
    else:
        return self.create_line(DIM/2-l+1, DIM/2+1, DIM/2+l+1, DIM/2+1, **kwargs)

def _draw_vertical(self, l, **kwargs):
    l = l / DIA * DIM
    if "width" in kwargs.keys():
        w = kwargs["width"] / DIA * DIM
        del kwargs["width"]
        return self.create_line(DIM/2+1, DIM/2-l+1, DIM/2+1, DIM/2+l+1, width=w, **kwargs)
    else:
        return self.create_line(DIM/2+1, DIM/2-l+1, DIM/2+1, DIM/2+l+1, **kwargs)
AREA10 = 40
AREA9 = 80
AREA8 = 120
AREA7 = 160
AREA6 = 200
AREA5 = 240
AREA4 = 280
AREA3 = 320
AREA2 = 360
AREA1 = 400

def draw_scoreboard(canvas):
    canvas.draw_circle = types.MethodType(_draw_circle, canvas)
    canvas.draw_horizon= types.MethodType(_draw_horizon, canvas)
    canvas.draw_vertical= types.MethodType(_draw_vertical, canvas)
    canvas.draw_circle(r=AREA1, fill="white", outline="black", width=0.2)
    canvas.draw_circle(r=AREA2, fill="white", outline="black", width=0.2)
    canvas.draw_circle(r=AREA3, fill="black")
    canvas.draw_circle(r=AREA4, fill="black", outline="white", width=0.2)
    canvas.draw_circle(r=AREA5, fill="#41b7c8")    
    canvas.draw_circle(r=AREA6, fill="#41b7c8", outline="black", width=0.2)
    canvas.draw_circle(r=AREA7, fill="#fd1b14", outline="black", width=0.2)
    canvas.draw_circle(r=AREA8, fill="#fd1b14", outline="black", width=0.2)
    canvas.draw_circle(r=AREA9, fill="#fff535", outline="black", width=0.2)
    canvas.draw_circle(r=AREA10, fill="#fff535", outline="black", width=0.2)
    canvas.draw_circle(r=AREA10/2, fill="#fff535", outline="black", width=0.1)
    # draw cross
    canvas.draw_horizon(l=5, fill="black", width=0.1)
    canvas.draw_vertical(l=5, fill="black", width=0.1)

def estimate_score(pos):
    r = sqrt(pos[0]**2 + pos[1]**2)
    if(r <= AREA10): score = 10
    elif(r <= AREA9): score = 9
    elif(r <= AREA8): score = 8
    elif(r <= AREA7): score = 7
    elif(r <= AREA6): score = 6
    elif(r <= AREA5): score = 5
    elif(r <= AREA4): score = 4
    elif(r <= AREA3): score = 3
    elif(r <= AREA2): score = 2
    elif(r <= AREA1): score = 1
    else: score = 0
    return score