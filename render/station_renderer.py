#! /usr/bin/env python3
# coding: utf-8

from tkinter import Canvas


class StationRenderer:

    def __init__(self, station, master):
        assert station != None and master != None
        self.station = station
        self.master = master
        self.is_text_written = False
        # creating canvas
        self.make_canvas()

    def update_canvas(self):
        assert self.canvas != None
        color = "#00FF00" if self.is_selected else "blue"
        self.canvas.create_oval(self.outline_width, self.outline_width, self.width - self.outline_width,
                                self.height - self.outline_width, outline=color, width=self.outline_width)
        if not self.is_text_written:  # otherwise text become ugly :/
            self.canvas.create_text(self.width / 2, self.height / 2, text=self.station.id, tags="text")
            self.is_text_written = True
        self.canvas["bg"] = self.master["bg"]

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
            r = self.width / 2
            # and updating is_selected (circle equation)
            self.is_selected = ((event.x - xr) ** 2 + (event.y - yr) ** 2) <= r * r
            self.master.update_selected_item(self)
            return

        self.canvas.bind("<Button-1>", callback)

        # updating canvas
        self.update_canvas()
