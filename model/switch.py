#! /usr/bin/env python3
# coding: utf-8

import model.routing
from config import config

switch_id = 0
timer_other = int(config.routing('timer_other'))
my_timer = int(config.routing('my_timer'))

switches = []
alive_timers = []


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

    def __init__(self, loop, other_loop, previous_station=None, next_station= None, next_station_other=None, size=200):
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
        self.direct_defects = [False, False]
        global switches
        switches += [self]
        global alive_timers
        alive_timers += [float('inf'), float('inf')]

    def _change_state(self):
        self.isRoutingToLoop = not self.is_routing_to_loop
        return

    def route_capsule_to_station(self, capsule, station):
        l = station.loop
        if self.table[l.name]: #il faut qu'elle change de boucle
            self.is_routing_to_loop = True
            capsule.current_station = None
            return True
            #capsule._change_loop(self.next_station)
        else :
            #capsule._do_a_loop(self.next_station_other)
            return False


def init():
    for s in switches:
        s.timers = [timer_other for i in range(0, switch_id)]
        s.timers[s.id] = my_timer
        s.defects = [[False, False] for i in range(switch_id)]
    for s in switches:
        s.table = model.routing.parcours(s, s.permanent_table, s.permanent_cover)
        # FINAL
        s.permanent_table = s.table

        # anomalies des switches : [boucle presente, boucle aiguillee] True ==> anomalies


def update():
    for s in switches:
        #if s.is_routing_to_loop:
        info = model.routing.update_switch(s)
