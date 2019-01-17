#! /usr/bin/env python3
# coding: utf-8

from tkinter import Canvas

class LoopRenderer:
    def __init__(self, loop, master):
        assert loop != None and master != None
        self.loop = loop
        self.master = master
        # creating canvas
        self.make_canvas()
    
    def update_canvas(self):
        # TODO
        return
    
    def make_canvas(self):
        # if canvas is selected
        self.is_selected = False

        # building canvas
        self.dim = 2*self.loop.r
        self.canvas = Canvas(self.master, width=self.dim, height=self.dim)

        def callback(event):
            # checking if click happened inside donut or not
            # TODO
            # and updating is_selected (donut equation)
            #self.is_selected = ((event.x - xr)**2 + (event.y - yr)**2) <= r*r
            #self.master.update_selected_item(self)
            return
        self.canvas.bind("<Button-1>", callback)

        # updating canvas
        self.update_canvas()