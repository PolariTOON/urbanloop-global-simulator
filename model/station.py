#! /usr/bin/env python3
# coding: utf-8

station_id = 0


class Station:
    # capsules
    capsules_in_slots = None
    # network
    network = None

    def __init__(self, name=None, capacity=1, previous_station=None, next_station=None, loop=None):
        global station_id
        self.id = station_id
        station_id += 1
        # properties
        self.name = "Station #{0}".format(self.id) if (name is None) else name
        self.capacity = capacity
        self.previous_station = previous_station
        self.next_station = next_station
        self.loop = loop

    def _update_flow(self):
        print("updating flow of ", self.id, "...")
        return

    def show_details(self):
        print("showing details...")
        print("\n \t id = ", self.id, "\n \t name = ", self.name)
        return
