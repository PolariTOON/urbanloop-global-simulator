#! /usr/bin/env python3
# coding: utf-8

all_loops = {}

class Loop:
    def __init__(self, name, stations=None, switchs=None):
        '''global loop_id
        self.id = loop_id
        loop_id += 1'''
        self.name = name
        self.stations = stations
        self.switchs = None
        global all_loops
        all_loops[self.name] = self


def get_by_name(search_name):
    for name, loop in all_loops.items():
        if name == search_name:
            return loop
    return None
