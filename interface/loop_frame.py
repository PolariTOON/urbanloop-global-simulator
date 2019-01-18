#! /usr/bin/env python3
# coding: utf-8

from tkinter import Frame

class LoopFrame(Frame):
    def __init__(self, master, network=None):
        Frame.__init__(self)
        # checking if called correctly
        assert master != None
        self.master = master
        self.network = network
    
    def update_selected_item(self, item):
        self.master.update_selected_item(item)