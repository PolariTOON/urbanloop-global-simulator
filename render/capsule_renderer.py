#! /usr/bin/env python3
# coding: utf-8

from tkinter import Canvas


class CapsuleRenderer:

    def __init__(self, capsule, master):
        """TODO baptiste specification """
        assert capsule is not None and master is not None
        self.capsule = capsule
        self.master = master
        # creating canvas
        self.make_canvas()

    def update_canvas(self):
        """TODO baptiste specification """
        assert self.canvas is not None
        color = "#00FF00" if self.is_selected else "red"
        self.canvas.create_oval(self.outline_width, self.outline_width, self.width - self.outline_width,
                                self.height - self.outline_width, fill=color, outline="black", width=self.outline_width)
        self.canvas["bg"] = self.master["bg"]

    def make_canvas(self, w=20, h=20, ow=1):
        """TODO baptiste specification """
        # checking if function is correctly called
        assert w > 0 and h > 0 and ow > 0
        self.outline_width = ow  # TODO baptiste variable pas initialisee dans _init ?
        self.width = w  # TODO baptiste variable pas initialisee dans _init ?
        self.height = h  # TODO baptiste variable pas initialisee dans _init ?

        # if capsule is selected
        self.is_selected = False  # TODO baptiste variable pas initialisee dans _init ?

        # building canvas and adding event listener
        self.canvas = Canvas(self.master, width=w, height=h)  # TODO baptiste variable pas initialisee dans _init ?

        def callback(event):
            """TODO baptiste specification """
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
