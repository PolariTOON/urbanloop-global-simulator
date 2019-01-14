#! /usr/bin/env python3
# coding: utf-8

class Switch:
    # network
    network = None
    is_routing_to_loop = False

    def __init__(self, loop, next_stops):
        self.loop = loop
        self.next_stops = next_stops

    def _change_state(self):
        self.is_routing_to_loop = not self.is_routing_to_loop
        return

    def route_capsule_to_station(self, capsule, station):
        # TODO
        return
