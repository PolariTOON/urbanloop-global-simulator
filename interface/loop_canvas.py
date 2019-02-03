#! /usr/bin/env python3
# coding: utf-8

from tkinter import Canvas


class LoopCanvas(Canvas):
    """
    constructeur; il s'agit d'un artifice pour ajouter la fonction
    update_selected_item a un Canvas. l'architecture mérite d'etre
    revue globalement, mais on se contente de ça dans l'immédiat
    param width: largeur de self.canvas
    param height: largeur de self.canvas
    param master: la Frame dans laquelle est dessiné self.canvas
    """
    def __init__(self, width, height, master):
        self.width = width
        self.height = height
        super().__init__(width=self.width, height=self.height, highlightthickness=0)
        self.master = master
    
    """
    relaie la tâche à la Frame supérieure, à savoir à une SimulatorFrame
    """
    def update_selected_item(self, item):
        self.master.update_selected_item(item)
