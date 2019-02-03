#! /usr/bin/env python3
# coding: utf-8

from model import loop as ML

class Handler:
    def __init__(self, root):
        assert root != None
        self.loops = ML.all_loops
        self.root = root
        self.selected_item = None
    
    def update_simulator_view(self):
        sim = self.root
    
    def update_selected_item(self, item):
        if (self.selected_item == item):
            self.selected_item = None
        else:
            self.selected_item = item
        self.update_simulator_view()
