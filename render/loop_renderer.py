#! /usr/bin/env python3
# coding: utf-8

from tkinter import Canvas
from math import pi


class LoopRenderer:
    def __init__(self, loop, master):
        """TODO baptiste specification """
        assert loop is not None and master is not None
        self.loop = loop
        self.master = master
        # creating canvas
        self.make_canvas(self.loop.size)

    def update_canvas(self):
        """TODO baptiste specification """
        assert self.canvas is not None
        # circle
        color = "#00FF00" if self.is_selected else "#a0a0a0"
        self.canvas.create_oval(0, 0, self.outline_width, self.outline_width, self.dim - self.outline_width,
                                self.dim - self.outline_width,
                                outline=color, width=self.outline_width)
        self.canvas["bg"] = self.master["bg"]
        # objects
        # TODO

    def make_canvas(self, c, ow=4):
        """TODO baptiste specification """
        # checking if function is correctly called
        assert c > 0 and ow > 0
        self.outline_width = ow
        self.dim = c / pi

        # if canvas is selected
        self.is_selected = False

        # building canvas
        self.canvas = Canvas(self.master, width=self.dim, height=self.dim)

        def callback(event):
            """TODO baptiste specification """
            # checking if click happened inside donut or not
            # TODO
            # and updating is_selected (donut equation)
            # self.is_selected = ((event.x - xr)**2 + (event.y - yr)**2) <= r*r
            # self.master.update_selected_item(self)
            return

        self.canvas.bind("<Button-1>", callback)

        # updating canvas
        self.update_canvas()
