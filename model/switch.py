#! /usr/bin/env python3
# coding: utf-8

import model.routing
from settings import config

switch_id = 0
timer_other = int(config.routing['timer_other'])
my_timer = int(config.routing['my_timer'])
switched_cost = int(config.routing['switched_cost'])

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
    angle_my_loop = None
    angle_other_loop = None

    timers = None
    defects = None

    def __init__(self, loop=None, other_loop=None, previous_station=None, next_station=None, next_station_other=None,
                 size=switched_cost):
        global switch_id
        self.id = switch_id
        switch_id += 1
        self.my_loop = loop
        self.last_station = previous_station
        self.next_station = next_station
        self.other_loop = other_loop
        self.other_loop_station = next_station_other
        self.size = size
        self.my_defects = [False, False]
        global switches
        switches += [self]
        global alive_timers
        alive_timers += [float('inf'), float('inf')]

    def _change_state(self):
        self.isRoutingToLoop = not self.is_routing_to_loop
        return

    def route_capsule_to_station(self, capsule, station):
        l = station.loop
        if self.table[l.name]:  # il faut qu'elle change de boucle
            self.is_routing_to_loop = True
            capsule.current_station = None
            return True
            # capsule._change_loop(self.next_station)
        else:
            # capsule._do_a_loop(self.next_station_other)
            return False


def init():
    for s in switches:
        s.permanent_table = {s.my_loop.name: [False, int((s.my_loop.size) / 2), [s.id, s.my_loop.name]],
                             s.other_loop.name: [True, s.size, [s.id, s.other_loop.name]]}
        s.permanent_cover = {s.my_loop.name: s.id, s.other_loop.name: s.id}
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
        # if s.is_routing_to_loop:
        info = model.routing.update_switch(s)
        # maj des timers suivant info
        if info == "alive":
            alive_timers[s.id] = [0, 0]
        elif info is None:
            alive_timers[s.id][0] += 1
            alive_timers[s.id][1] += 1
        else:
            if "0_down" in info:
                alive_timers[s.id][0] = [float("Inf")]
                alive_timers[s.id][1] += 1
            if info == "1_down":
                alive_timers[s.id][0] += 1
                alive_timers[s.id][1] = [float("Inf")]
