#! /usr/bin/env python3
# coding: utf-8

from tkinter import Frame


class SimulatorFrame(Frame):

    def __init__(self, master, network=None):
        """
        constructeur
        param master: son contenant (un objet Tk ou Frame)
        network: le simulateur
        """
        Frame.__init__(self)
        # checking if called correctly
        assert master is not None
        # attributes
        self.master = master
        self.network = network
        self.selected_item = None

        # unselect item

        def callback(event):  # TODO event not used
            """
            fonction triggered lors d'un clic dessus
            (à savoir pas sur un objet représenté)
            on désélectionne si un objet était sélectionné
            """
            if self.selected_item is not None:  # nothing to do else
                if self.selected_item.is_selected:
                    self.selected_item.is_selected = False
                    self.selected_item.update_canvas()
                self.selected_item = None
        self.bind("<Button-1>", callback)

    def update_selected_item(self, item):
        """
        met a jour le dernier objet sélectionné et le rafraichit
        ainsi que le précédent
        """
        # updating last selected item if there is one
        if self.selected_item is not None:
            self.selected_item.is_selected = False
            self.selected_item.update_canvas()
        # storing new one if it is selected
        if item is not None and item.is_selected:
            self.selected_item = item
            self.selected_item.is_selected = True
            self.selected_item.update_canvas()
            self.notify_master()
        else:
            self.selected_item = None

    def notify_master(self):
        """
        avertit la fenetre d'un changement pour mettre à
        jour le panel d'informations
        """
        # TODO
        # update data in the data field
        print("notify master: new selected item is ",self.selected_item)
        return
