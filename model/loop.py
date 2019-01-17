#! /usr/bin/env python3
# coding: utf-8
import numpy as np

all_loops = {}
default_size = 100


class Loop:
    def __init__(self, name, size=default_size, coordinates=None):
        self.name = name
        print("Create loop", self.name)
        if coordinates is not None:
            self.x = coordinates[0]
            self.y = coordinates[1]
        self.size = size

        global all_loops
        all_loops[self.name] = self
        self.stations = []
        self.switches = []

    def add_order(self, order):
        self.objects = []
        self.lengths = []
        for nature, obj, angle in order:
            self.objects += [obj]
            self.lengths += [int((angle/360)*self.size*np.pi)]
            '''if obj[0] == "switch":
                self.switches += obj[1]
            else:  # object[0]=="station":
                self.stations += obj[1]
            '''
            if self.size is None:
                self.size = sum(self.lengths)


def get_by_name(search_name):
    for name, loop in all_loops.items():
        if name == search_name:
            return loop
    return None
