#! /usr/bin/env python3
# coding: utf-8

from tkinter import Canvas

class SwitchRenderer:
    def __init__(self, switch, master):
        assert master != None and switch != None
        self.switch = switch
        self.master = master
        # creating canvas
        self.make_canvas()
    
    def update_canvas(self):
        assert self.canvas != None
        # station-like
        color = "#00FF00" if self.is_selected else "blue"
        self.canvas.create_oval(self.outline_width,self.outline_width,self.width-self.outline_width,self.height-self.outline_width,outline=color,width=self.outline_width)
        self.canvas["bg"] = self.master["bg"]
        # adding a X
        xr = self.width / 2
        yr = self.height / 2
        r = self.width/2
        min, max = self.width, 0 
        for x in range(1, self.width+1):
            if ((x - xr)**2 + (x - yr)**2) < r*r:
                if min > x:
                    min = x
                if max < x:
                    max = x
        self.canvas.create_line(min, min, max, max,fill=color,width=self.outline_width-1)
        self.canvas.create_line(min, max, max, min,fill=color,width=self.outline_width-1)
    
    def make_canvas(self, w=50, h=50, ow=3):
        # checking if function is correctly called
        assert w > 0 and h > 0 and ow > 0
        self.outline_width = ow
        self.width = w
        self.height = h

        # if canvas is selected
        self.is_selected = False

        # building canvas and adding event listener
        self.canvas = Canvas(self.master, width=w, height=h)
        def callback(event):
            # checking if click happened inside circle or not
            xr = self.width / 2
            yr = self.height / 2
            r = self.width/2
            # and updating is_selected (circle equation)
            self.is_selected = ((event.x - xr)**2 + (event.y - yr)**2) <= r*r
            self.master.update_selected_item(self)
            return
        self.canvas.bind("<Button-1>", callback)

        # updating canvas
        self.update_canvas()