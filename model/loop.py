#! /usr/bin/env python3
# coding: utf-8

all_loops = {}


class Loop:
    objects = None
    lenghts = None
    size = 0

    def __init__(self, name, stations=None, switches=None):
        self.name = name
        self.stations = stations
        self.switches = switches
        if stations is None :
            if switches is None :
                self.size = 100
            else :
                self.size += (len(switches)) * 10
        else :
            self.size += (len(stations))*10

        global all_loops
        all_loops[self.name] = self

    def add_order(self, order, lengths):
        for obj in order:
            self.objects += obj
            self.lenghts += lengths[order.indexof(order)]
            if obj[0] == "switch":
                self.switches += obj[1]
            else:  # object[0]=="station":
                self.stations += obj[1]
            self.size = sum(lengths)


def get_by_name(search_name):
    for name, loop in all_loops.items():
        if name == search_name:
            return loop
    return None
