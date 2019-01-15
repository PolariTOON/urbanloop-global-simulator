#! /usr/bin/env python3
# coding: utf-8

import Model.Routing

switch_id = 0
TIMER_OTHER = 60
MY_TIMER = 40

switches = []


class Switch:
    # network
    network = None
    is_routing_to_loop = False

    '''my_loop = None
    next_loop = None 
    size = 0 
    permanent_table = None'''

    timers = None
    defects = None

    def __init__(self, loop, other_loop, previous_station=None, next_station=None, size=200):
        global switch_id
        self.id = switch_id
        switch_id += 1
        self.my_loop = loop
        self.last_station = previous_station
        self.switched_loop = other_loop
        self.other_loop_station = next_station
        self.size = size
        self.permanent_table = {self.my_loop.name: [False, 0, [self.id, self.my_loop.name]],
                                self.switched_loop.name: [True, self.size, [self.id, self.switched_loop.name]]}
        self.permanent_cover = {self.my_loop.name: self.id, self.switched_loop.name: self.id}
        global switches
        switches += [self]

    def _change_state(self):
        self.isRoutingToLoop = not self.is_routing_to_loop
        return

    def route_capsule_to_station(self, capsule, station):
        # TODO
        return


def resume():
    for s in switches:
        s.timers = [TIMER_OTHER for i in range(0, switch_id)]
        s.timers[s.id] = MY_TIMER
        s.defects = [[False, False] for i in range(switch_id)]
    for s in switches:
        s.table = Model.Routing.parcours(s, s.permanent_table, s.permanent_cover)
        # FINAL
        s.permanent_table = s.table

        # anomalies des switches : [boucle presente, boucle aiguillee] True ==> anomalies
