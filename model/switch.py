#! /usr/bin/env python3
# coding: utf-8
import logging

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

    def __init__(self, loop=None, angle=None, other_loop=None, previous_element=None, next_element=None,
                 next_element_other=None, size=switched_cost):
        """
        initialisation d'un aiguillage
        :param  loop : boucle où le switch est présent (Loop)
        :param  other_loop : boucle aiguillée (Loop)
        :param  previous_element : l'element avant le switch de la loop où le switch est (Station/Switch)
        :param  next_element : la station après le switch sur la loop où le switch est (Station/Switch)
        :param  next_element_other : la station après le switch sur la loop aiguillée (Station/Switch)
        :param  size : la taille de l'aiguillage
        :return:0UT : un objet aiguillage (Switch)
        """
        global switch_id
        self.id = switch_id
        switch_id += 1
        self.my_loop = loop
        self.angle = angle
        self.last_element = previous_element
        self.next_element = next_element
        self.other_loop = other_loop
        self.next_element_other = next_element_other
        self.angle_my_loop = None
        self.angle_other_loop = None
        self.size = size
        self.my_defects = [False, False]
        self.defects = []
        global switches
        switches += [self]
        global alive_timers
        alive_timers += [float('inf'), float('inf')]
        self.timers = []
        self.table = {}

    '''def _change_state(self):
        self.isRoutingToLoop = not self.is_routing_to_loop
        return
    '''

    def route_capsule_to_station(self, station):
        """
        la fonction qu'une capsule déclenche lorsqu'elle arrive sur le switch et souhaite être routée
            :param  station: la station de destination vers laquelle la capsule souhaite aller (Station) OBLIGATOIRE
            :return: OUT : True si la capsule doit changer de loop, False sinon (boolean)
            """
        the_loop = station.loop
        if self.table[the_loop.name][0]:  # il faut qu'elle change de boucle
            logging.debug("le switch " + str(self.id) + " aiguille la capsule voulant aller à " + station.name
                          + " depuis la boucle " + self.my_loop.name + " sur la boucle " + self.other_loop.name)
            # self.is_routing_to_loop = True
            return True
            # capsule._change_loop(self.next_element)
        else:
            logging.debug("le switch " + str(self.id) + " laisse la capsule voulant aller à " + station.name
                          + " sur la boucle " + self.my_loop.name)
            # capsule._do_a_loop(self.next_element_other)
            return False


def init():
    """
    fonction d'initialisation de tous les switchs pour que la taille des tableaux correspondant à tous les objets prévus
        :return: 0UT : (void) modification des attributs intrinsèques aux switchs
    """
    for s in switches:
        s.permanent_table = {s.my_loop.name: [False, 0, [s.id, s.my_loop.name]],
                             s.other_loop.name: [True, s.size, [s.id, s.other_loop.name]]}
        s.permanent_cover = {s.my_loop.name: s.id, s.other_loop.name: s.id}
        s.timers = [timer_other for i in range(0, switch_id)]
        s.timers[s.id] = my_timer
        s.defects = [[False, False] for i in range(switch_id)]
    for s in switches:
        s.table = model.routing.dijkstra_route(s, s.permanent_table, s.permanent_cover)
        # FINAL
        s.permanent_table = s.table

        # anomalies des switches : [boucle presente, boucle aiguillee] True ==> anomalies


def update():
    """
     fonction qui est lancée à chaque tour pour actualiser les états des switchs et leur table (pour le routage)
        :return: (void) modifications des éléments, attributs des switches
    """
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
