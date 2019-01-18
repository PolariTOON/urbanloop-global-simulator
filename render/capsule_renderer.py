#! /usr/bin/env python3
# coding: utf-8

from tkinter import Canvas
from settings import config


class CapsuleRenderer:

    def __init__(self, capsule, master):
        """
        constructeur
        param capsule: capsule à afficher
        param master: Canvas sur lequel dessiner 
        """
        self.config = config.interface
        assert capsule is not None and master is not None
        self.capsule = capsule
        self.master = master
        # creating canvas
        self.make_canvas()

    def update_canvas(self):
        """
        mise a jour de la texture en fonction de l'état de la capsule
        """
        # TODO
        # faire bouger les capsules selon leurs déplacements
        assert self.canvas != None
        color = "#00FF00" if self.is_selected else "red"
        self.canvas.create_oval(self.outline_width, self.outline_width, self.width - self.outline_width,
                                self.height - self.outline_width, fill=color, outline="black", width=self.outline_width)
        self.canvas["bg"] = self.master["bg"]

    def make_canvas(self):
        """
        construit le canvas sur lequel dessiner et lui ajoute des listeners
        """
        self.outline_width = int(self.config["capsule_outline_width"]) # TODO baptiste variable pas initialisee dans _init ?
        self.width = int(self.config["capsule_width"])
        self.height = int(self.config["capsule_height"])

        # if capsule is selected
        self.is_selected = False  # TODO baptiste variable pas initialisee dans _init ?

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
            return
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
            if (self.is_above == True):
                self.canvas["cursor"]='hand2'
            else:
                self.canvas["cursor"]=''
        self.canvas.bind("<Motion>",motion)

        # updating canvas
        self.update_canvas()
