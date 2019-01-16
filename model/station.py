#! /usr/bin/env python3
# coding: utf-8
from enum import Enum

station_id = 0


class Type(Enum):
    NEUTRAL = 0
    ACTIVITY = 1
    RESIDENTIAL = 2
    CITY = 3


class Station:
    # capsules
    capsules_in_slots = None
    # network
    network = None

    def __init__(self, name=None, capacity=100, loop=None, angle=None, station_type=Type.NEUTRAL):
        global station_id
        self.id = station_id
        station_id += 1
        self.name = "Station #{0}".format(self.id) if (name is None) else name
        self.angle = angle
        self.capacity = capacity
        self.loop = loop
        self.station_type = station_type
        self.queue = 0

    def _update_flow(self):
        print("updating flow of ", self.id, "...")
        return

    def show_details(self):
        print("showing details...")
        print("\n \t id = ", self.id, "\n \t name = ", self.name)
        return
