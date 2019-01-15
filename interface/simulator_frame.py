#! /usr/bin/env python3
# coding: utf-8

from tkinter import Frame

class SimulatorFrame(Frame):
    def __init__(self, master, network=None):
        Frame.__init__(self)
        # checking if called correctly
        assert master != None
        # attributes
        self.master = master
        self.network = network
        self.selected_item = None
    
    def update_selected_item(self, item):
        # updating last selected item if there is one
        if self.selected_item != None:
            self.selected_item.is_selected = False
            self.selected_item.update_canvas()
        # storing new one
        self.selected_item = item
        self.selected_item.is_selected = True
        self.selected_item.update_canvas()
        self.notify_master()
    
    def notify_master(self):
        # TODO
        # update data in the data field
        print("notify master")
        return