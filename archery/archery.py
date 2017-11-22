import types

DIM = 400
DIA = 80.0

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

def draw_scoreboard(canvas):
    canvas.draw_circle = types.MethodType(_draw_circle, canvas)
    canvas.draw_horizon= types.MethodType(_draw_horizon, canvas)
    canvas.draw_vertical= types.MethodType(_draw_vertical, canvas)
    canvas.draw_circle(r=39.9, fill="white", outline="black", width=0.2)
    canvas.draw_circle(r=35.9, fill="white", outline="black", width=0.2)
    canvas.draw_circle(r=32.0, fill="black")
    canvas.draw_circle(r=27.9, fill="black", outline="white", width=0.2)
    canvas.draw_circle(r=24.0, fill="#41b7c8")    
    canvas.draw_circle(r=19.9, fill="#41b7c8", outline="black", width=0.2)
    canvas.draw_circle(r=15.9, fill="#fd1b14", outline="black", width=0.2)
    canvas.draw_circle(r=11.9, fill="#fd1b14", outline="black", width=0.2)
    canvas.draw_circle(r=7.9, fill="#fff535", outline="black", width=0.2)
    canvas.draw_circle(r=3.9, fill="#fff535", outline="black", width=0.2)
    canvas.draw_circle(r=1.9, fill="#fff535", outline="black", width=0.1)
    # draw cross
    canvas.draw_horizon(l=0.4, fill="black", width=0.1)
    canvas.draw_vertical(l=0.4, fill="black", width=0.1)
