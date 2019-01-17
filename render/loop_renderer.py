#! /usr/bin/env python3
# coding: utf-8

from model.station import Station
from model.switch import Switch

from render.station_renderer import StationRenderer
from render.switch_renderer import SwitchRenderer

from tkinter import Canvas
from settings import config
from math import pi, cos, sin

class LoopRenderer:
    def __init__(self, loop, master):
        self.config = config.interface
        assert loop != None and master != None
        self.loop = loop
        self.master = master
        # creating canvas
        self.make_canvas()
    
    def update_canvas(self):
        assert self.canvas != None
        # circle
        color = self.config["selected_color"] if self.is_selected else self.config["loop_color"]
        self.canvas.create_oval(self.outline_width, self.outline_width, self.dim-self.outline_width, self.dim-self.outline_width,
                        outline=color,width=self.outline_width)
        self.canvas["bg"]=self.master["bg"]
        # objects
        angle=0
        print("ca part")
        for object in self.loop.objects:
            if not (isinstance(object, Switch) or isinstance(object, Station)):
                # TODO
                print("?")
            else:
                # TODO
                angle+=object.angle
                x = self.dim/2 * (1 + cos((angle*2*pi)/360))
                y = self.dim/2 * (1 - sin((angle*2*pi)/360)) 
                print(object)
                print("  at [{0};{1}]".format(x, y))
                renderer = StationRenderer(object, self.canvas) if isinstance(object, Station) else SwitchRenderer(object, self.canvas)
                canvas = renderer.canvas
                canvas.place(x=x-renderer.width,y=y-renderer.height)
    
    def make_canvas(self):
        self.outline_width = int(self.config["loop_outline_width"])
        self.dim = int(self.config["loop_circumference"])/pi

        # if canvas is selected
        self.is_selected = False

        # building canvas
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