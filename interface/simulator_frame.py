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
        # unselect item
        def callback(event):
            print("callback")
            if self.selected_item != None: # nothing to do else
                if (self.selected_item.is_selected == True):
                    self.selected_item.is_selected = False
                    self.selected_item.update_canvas()
                self.selected_item = None
        self.bind("<Button-1>", callback)
    
    def update_selected_item(self, item):
        # updating last selected item if there is one
        if self.selected_item != None:
            self.selected_item.is_selected = False
            self.selected_item.update_canvas()
        # storing new one if it is selected
        if (item != None and item.is_selected == True):
            self.selected_item = item
            self.selected_item.is_selected = True
            self.selected_item.update_canvas()
            self.notify_master()
        else:
            self.selected_item = None
    
    def notify_master(self):
        # TODO
        # update data in the data field
        print("notify master")
        return