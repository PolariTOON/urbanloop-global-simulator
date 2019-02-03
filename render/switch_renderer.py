#! /usr/bin/env python3
# coding: utf-8

from tkinter import Canvas
from settings import config


class SwitchRenderer:
    def __init__(self, switch, master):
        """TODO baptiste specification """
        self.config = config.interface
        assert master is not None and switch is not None
        self.switch = switch
        self.master = master
        # creating canvas
        self.make_canvas()

    def update_canvas(self):
        """
        mise a jour de la texture en fonction de l'état de la capsule
        """
        assert self.canvas is not None
        # station-like
        color = self.config["selected_color"] if self.is_selected else self.config["switch_color"]
        self.canvas.create_oval(self.outline_width, self.outline_width, self.width - self.outline_width,
                                self.height - self.outline_width, outline=color, width=self.outline_width)
        self.canvas["bg"] = self.master["bg"]
        # adding a X
        xr = self.width / 2
        yr = self.height / 2
        r = self.width / 2
        min, max = self.width, 0
        for x in range(1, self.width + 1):
            if ((x - xr) ** 2 + (x - yr) ** 2) < r * r:
                if min > x:
                    min = x
                if max < x:
                    max = x
        self.canvas.create_line(min, min, max, max, fill=color, width=self.outline_width - 1)
        self.canvas.create_line(min, max, max, min, fill=color, width=self.outline_width - 1)

    def make_canvas(self):
        """
        construit le canvas sur lequel dessiner et lui ajoute des listeners
        """
        # TODO variables pas dans le _init
        self.outline_width = int(self.config["switch_outline_width"])
        self.width = int(self.config["switch_width"])
        self.height = int(self.config["switch_height"])

        # if canvas is selected
        self.is_selected = False

        # building canvas and adding event listener
        self.canvas = Canvas(self.master, width=self.width, height=self.height, highlightthickness=0)

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
            # and updating is_above (circle equation)
            self.is_above = ((event.x - xr) ** 2 + (event.y - yr) ** 2) <= r * r
            if self.is_above:
                self.canvas["cursor"] = 'hand2'
            else:
                self.canvas["cursor"] = ''

        self.canvas.bind("<Motion>", motion)

        # updating canvas
        self.update_canvas()
