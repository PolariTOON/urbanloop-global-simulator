#! /usr/bin/env python3
# coding: utf-8

from tkinter import Canvas

class CapsuleRenderer:

    def __init__(self, capsule, master):
        assert capsule != None and master != None
        self.capsule = capsule
        self.master = master
        # creating canvas
        self.make_canvas()
    
    def update_canvas(self):
        assert self.canvas != None
        color = "#00FF00" if self.is_selected else "red"
        self.canvas.create_oval(self.outline_width,self.outline_width,self.width-self.outline_width,self.height-self.outline_width,fill=color,outline="black",width=self.outline_width)
        self.canvas["bg"] = self.master["bg"]
    
    def make_canvas(self, w=20, h=20, ow=1):
        # checking if function is correctly called
        assert w > 0 and h > 0 and ow > 0
        self.outline_width = ow
        self.width = w
        self.height = h

        # if capsule is selected
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