#! /usr/bin/env python3
# coding: utf-8
import model.routing
from settings import config
from settings import simlog

switch_id = 0
timer_other = int(config.routing['timer_other'])
my_timer = int(config.routing['my_timer'])
switched_cost = int(config.routing['switched_cost'])

_switches = []
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
        :param  previous_element : l'element avant le switch de la station où le switch est (Station/Switch)
        :param  next_element : la station après le switch sur la station où le switch est (Station/Switch)
        :param  next_element_other : la station après le switch sur la station aiguillée (Station/Switch)
        :param  size : la taille de l'aiguillage
        :return: 0UT : un objet aiguillage (Switch)
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
        self.name = "Switch n°%d" % self.id
        global _switches
        _switches += [self]
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
            :return: OUT : True si la capsule doit changer de station, False sinon (boolean)
            """
        the_loop = station.loop
        return self.table[the_loop.name][0]
        # if self.table[the_loop.name][0]:  # il faut qu'elle change de boucle
        #     simlog.debug("le switch " + str(self.objectId) + " aiguille la capsule voulant aller à " + station.name
        #                  + " depuis la boucle " + self.my_loop.name + " sur la boucle " + self.other_loop.name)
        #     return True
        # else:
        #      simlog.debug("le switch " + str(self.objectId) + " laisse la capsule voulant aller à " + station.name
        #                   + " sur la boucle " + self.my_loop.name)
        #      return False

    def show_details(self):
        """
        crée un text contenant toutes les informations à propos de l'aiguillage
        :return: String
        """
        details = "Switch ID : " + str(self.id)
        details += "\nLoop of the switch : " + self.my_loop.name
        details += "\n \t Next element : "
        if type(self.next_element) is Switch:
            details += "Switch " + str(self.next_element.id)
        else:
            details += "Station " + self.next_element.name
        details += "\nLoop switched : " + self.other_loop.name
        details += "\n \t Next element : "
        if type(self.next_element_other) is Switch:
            details += "Switch " + str(self.next_element_other.id)
        else:
            details += "Station " + self.next_element_other.name
        details += "\nSize of the link : " + str(self.size)
        details += "\nRouting Table : " + str(self.table)
        return details

    def is_switch_out(self, the_loop):
        if the_loop is self.my_loop:
            return True
        elif the_loop is self.other_loop:
            return False
        else:
            simlog.error("The switch %d is not in the station %s" % (str(self.id), the_loop.name))


def init():
    """
    fonction d'initialisation de tous les switchs pour que la taille des tableaux correspondant à tous les objets prévus
        :return: 0UT : (void) modification des attributs intrinsèques aux switchs
    """
    for s in _switches:
        s.permanent_table = {s.my_loop.name: [False, 0, [s.id, s.my_loop.name]],
                             s.other_loop.name: [True, s.size, [s.id, s.other_loop.name]]}
        s.permanent_cover = {s.my_loop.name: s.id, s.other_loop.name: s.id}
        s.timers = [timer_other for i in range(0, switch_id)]
        s.timers[s.id] = my_timer
        s.defects = [[False, False] for i in range(switch_id)]
    for s in _switches:
        s.table = model.routing.dijkstra_route(s, s.permanent_table, s.permanent_cover)
        # FINAL
        s.permanent_table = s.table

        # anomalies des switches : [boucle presente, boucle aiguillee] True ==> anomalies


def update():
    """
     fonction qui est lancée à chaque tour pour actualiser les états des switchs et leur table (pour le routage)
        :return: (void) modifications des éléments, attributs des switches
    """
    for s in _switches:
        # if s.is_routing_to_loop:
        info = model.routing.update_switch(s)
        # maj des timers suivant infoIn
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


def get_switches():
    """
    :return: All switches of the network
    """
    return _switches
