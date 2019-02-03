#! /usr/bin/env python3
# coding: utf-8

from tkinter import Canvas
from settings import config


class StationRenderer:

    def __init__(self, station, master):
        """TODO baptiste specification """
        self.config = config.interface
        assert station is not None and master is not None
        self.station = station
        self.master = master
        self.is_text_written = False
        # creating canvas
        self.make_canvas()

    def update_canvas(self):
        """
        mise a jour de la texture en fonction de l'état de la capsule
        """
        assert self.canvas is not None
        color = self.config["selected_color"] if self.is_selected else self.config["station_color"]
        self.canvas.create_oval(self.outline_width, self.outline_width, self.width - self.outline_width,
                                self.height - self.outline_width, outline=color, width=self.outline_width)
        if not self.is_text_written:  # otherwise text become ugly :/
            self.canvas.create_text(self.width / 2, self.height / 2, text=self.station.id, tags="text")
            self.is_text_written = True
        # self.canvas["-transparentcolor"] = "TRANSCOLOUR"

    def make_canvas(self):
        """
        construit le canvas sur lequel dessiner et lui ajoute des listeners
        """
        self.outline_width = int(self.config["station_outline_width"])
        self.width = int(self.config["station_width"])
        self.height = int(self.config["station_height"])

        # if canvas is selected
        self.is_selected = False

        # building canvas and adding event listener
        self.canvas = Canvas(self.master, width=self.width, height=self.height, highlightthickness=0)
        self.canvas["bg"] = self.master["bg"]

        def callback(event):
            """
            listener de clic
            """
            # checking if click happened inside circle or not
            xr = self.width / 2
            yr = self.height / 2
            r = self.width / 2
            # and updating is_selected (circle equation)
            self.is_selected = ((event.x - xr) ** 2 + (event.y - yr) ** 2) <= r * r
            self.master.update_selected_item(self)

        self.canvas.bind("<Button-1>", callback)

        def motion(event):
            """
            listener de mouvement
            """
            # checking if cusor is above circle or not
            xr = self.width / 2
            yr = self.height / 2
            r = self.width / 2
            # and updating is_above
            self.is_above = ((event.x - xr) ** 2 + (event.y - yr) ** 2) <= r * r
            if self.is_above:
                self.canvas["cursor"] = 'hand2'
            else:
                self.canvas["cursor"] = ''

        self.canvas.bind("<Motion>", motion)

        # updating canvas
        self.update_canvas()
