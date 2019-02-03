#! /usr/bin/env python3
# coding: utf-8

from model.station import Station
from model.switch import Switch

from render.station_renderer import StationRenderer
from render.switch_renderer import SwitchRenderer

from interface.loop_canvas import LoopCanvas

from tkinter import Canvas
from settings import config
from math import pi, cos, sin


class LoopRenderer:
    def __init__(self, loop, master):
        """
        constructeur
        param loop: loop à dessiner
        param master: canvas sur lequel dessiner
        """
        self.config = config.interface
        assert loop is not None and master is not None
        self.loop = loop
        self.master = master
        # creating canvas
        self.make_canvas()

    def update_canvas(self):
        """
        mise a jour de la texture en fonction de l'état de la capsule
        """
        assert self.canvas is not None
        # circle
        color = self.config["selected_color"] if self.is_selected else self.config["loop_color"]
        self.canvas.create_oval(self.outline_width + self.offset, self.outline_width + self.offset,
                                self.dim - self.outline_width - self.offset,
                                self.dim - self.outline_width - self.offset,
                                outline=color, width=self.outline_width)
        # objects
        angle = 0
        for obj in self.loop.objects:
            if not (isinstance(obj, Switch) or isinstance(obj, Station)):
                # TODO
                print("something is wrong with the network. Things may go wrong")
            else:
                # TODO
                angle += obj.angle
                x = self.xr + self.r * cos((angle * 2 * pi) / 360)
                y = self.yr - self.r * sin((angle * 2 * pi) / 360)
                # print(object," at [{0};{1}]".format(x, y))
                renderer = StationRenderer(obj, self.canvas) if isinstance(obj, Station) else SwitchRenderer(
                    obj, self.canvas)
                canvas = renderer.canvas
                canvas.place(x=x - renderer.width / 2, y=y - renderer.height / 2, bordermode="outside")

    def make_canvas(self):
        """
        construit le canvas sur lequel dessiner et lui ajoute des listeners
        """
        # TODO baptiste variable pas initialisee dans _init ?
        self.outline_width = int(self.config["loop_outline_width"])
        diam = int(self.config["loop_circumference"]) / pi
        self.offset = diam * 0.075
        self.dim = self.offset * 2 + diam

        # if canvas is selected
        self.is_selected = False  # TODO baptiste variable pas initialisee dans _init ?

        # building canvas TODO baptiste variable pas initialisee dans _init ?
        self.canvas = LoopCanvas(master=self.master, width=self.dim, height=self.dim)
        self.canvas["bg"] = self.master["bg"]

        self.xr = self.dim / 2  # * (1 + cos((angle*2*pi)/360))
        self.yr = self.dim / 2  # * (1 - sin((angle*2*pi)/360))
        self.r = (self.dim - 2 * self.offset) / 2

        def callback(event):
            """
            listener de clic
            """
            # checking if click happened inside donut or not
            square_dist = (event.x - self.xr) ** 2 + (event.y - self.yr) ** 2
            # and updating is_selected (donut equation)
            self.is_selected = self.r ** 2 >= square_dist >= (self.r - self.outline_width * 2) ** 2
            # simplification de :
            # self.is_selected = square_dist <= self.r ** 2 and square_dist >= (self.r - self.outline_width * 2) ** 2
            self.master.update_selected_item(self)

        self.canvas.bind("<Button-1>", callback)

        def motion(event):
            """
            listener de mouvement
            """
            # checking if cursor is above donut or not
            square_dist = (event.x - self.xr) ** 2 + (event.y - self.yr) ** 2
            # and updating is_above
            self.is_above = self.r ** 2 >= square_dist >= (self.r - self.outline_width) ** 2
            # simplification de :
            # self.is_above = square_dist <= self.r ** 2 and square_dist >= (self.r - self.outline_width) ** 2
            if self.is_above:
                self.canvas["cursor"] = 'hand2'
            else:
                self.canvas["cursor"] = ''

        self.canvas.bind("<Motion>", motion)

        # updating canvas
        self.update_canvas()
