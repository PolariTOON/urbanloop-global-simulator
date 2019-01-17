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
        self.objects = []
        self.lengths = []

    def add_order(self, order):
        self.objects = []
        self.lengths = []
        for i in range(len(order)):
            element = order[i]
            # order[i] = [nature, obj, angle]
            self.objects += [order[i]]
            angle_next = order[(i+1)%len(order)][2]-element[2]
            if angle_next < 0 :
                angle_next += 360
            self.lengths += [float(angle_next/360)*self.size] # arc = 2*D*pi*angle/360  et D = circonference/pi
            if self.size is None:
                self.size = sum(self.lengths)

    def dist_to_next_object(self, object):
        #print(object)
        for i in range(len(self.objects)):
            #print(self.objects[i][1] == object)
            if self.objects[i][1] is object:
                return self.lengths[i], self.objects[i+1][1]
        return None


def get_by_name(search_name):
    for name, loop in all_loops.items():
        if name == search_name:
            return loop
    return None
