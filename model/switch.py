import numpy as np

from model import identifier, controller
from model import routing
from model import switch as model_switch
from model import controller
from settings import config
from settings import simlog

timer_other = int(config.routing['timer_other'])
my_timer = int(config.routing['my_timer'])
switched_cost = int(config.routing['switched_cost'])

_switches = []
alive_timers = []


class Switch:
    def __init__(self, loop=None, angle=-1, other_loop=None, previous_element=None, next_element=None,
                 next_element_other=None, size=switched_cost,rules = None):
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
        global _switches
        global alive_timers
        _switches.append(self)
        alive_timers += [float('inf'), float('inf')]

        self.uuid = identifier.generate_unique()
        self.id = identifier.generate_switch_id()
        self.my_loop = loop
        self.loop = self.my_loop
        self.angle = angle
        # self.last_element = previous_element
        self.next_element = next_element
        self.other_loop = other_loop
        self.next_element_other = next_element_other
        self.angle_my_loop = None
        self.angle_other_loop = None
        self.size = size
        self.my_defects = [False, False]
        self.defects = []
        self.name = "Switch n°%d" % self.id
        self.timers = []
        self.table = {}
        self.section_my_loop = None
        self.section_other_loop = None
        self.rules = []
        if rules is not None :
            self.rules == rules

    def route_capsule_to_station(self, capsule):
        """
        la fonction qu'une capsule déclenche lorsqu'elle arrive sur le switch et souhaite être routée
            :param  capsule: la capsule qui demande a être routée OBLIGATOIRE
            :return: OUT : True si la capsule doit changer de route, False sinon (boolean)
        """
        # the_loop = station.loop

        for rule in self.rules:
            if rule.match(self.id, capsule.loop.id, capsule.destination, capsule.priority, len(capsule.travelers)==0):
                controller.get_controller().update_from_switch(capsule)
                return rule.change

        print("NO MATCHING RULE : STAY ON SAME LOOP")
        return False
        # if self.table[the_loop.name][0]:  # il faut qu'elle change de boucle
        #     simlog.debug("le switch " + str(self.objectId) + " aiguille la capsule voulant aller à " + station.name
        #                  + " depuis la boucle " + self.my_loop.name + " sur la boucle " + self.other_loop.name)
        #     return True
        # else:
        #      simlog.debug("le switch " + str(self.objectId) + " laisse la capsule voulant aller à " + station.name
        #                   + " sur la boucle " + self.my_loop.name)
        #      return False

    def capsule_passing(self, capsule):
        controller.get_controller().update_from_switch(capsule)

    def is_switch_out(self, the_loop):
        if the_loop is self.my_loop:
            return True
        elif the_loop is self.other_loop:
            return False
        else:
            simlog.error("The switch %d is not in the station %s" % (str(self.id), the_loop.name))

    def add_rule(self,rule,index=-1):
        if index == -1 :
            index = 0
        self.rules.insert(index,rule)

    def remove_rule(self,rule):
        self.rules.remove(rule)

    def modify_rule(self, new_rule, old_rule):
        index = self.rules.index(old_rule)
        self.remove_rule(old_rule)
        self.add_rule(new_rule, index)


def init():
    """
    fonction d'initialisation de tous les switchs pour que les longueur dépendent des coordonnées
    et que la taille des tableaux correspondant à tous les objets prévus
    puis création de la table de routage permanente
        :return: 0UT : (void) modification des attributs intrinsèques aux switchs
    """
    for a_switch in _switches:  #  lenght depend des coordonnées
        loop_out, loop_in = a_switch.my_loop, a_switch.other_loop
        r_out = loop_out.size / (2 * np.pi)
        r_in = loop_in.size / (2 * np.pi)
        x_out = loop_out.x + np.cos(np.deg2rad(a_switch.angle_my_loop)) * r_out
        y_out = loop_out.y + np.sin(np.deg2rad(a_switch.angle_my_loop)) * r_out
        x_in = loop_in.x + np.cos(np.deg2rad(a_switch.angle_other_loop)) * r_in
        y_in = loop_in.y + np.sin(np.deg2rad(a_switch.angle_other_loop)) * r_in
        a_switch.size = np.round(np.sqrt((x_out - x_in) ** 2 + (y_out - y_in) ** 2), 2)

    for a_switch in _switches:  # table de "nouvelles"
        a_switch.permanent_table = {a_switch.section_my_loop: [False, 0, [a_switch.id, a_switch.section_my_loop]],
                                    a_switch.section_other_loop: [True, a_switch.size,
                                                                  [a_switch.id, a_switch.section_other_loop]]}
        # print (a_switch.name, a_switch.permanent_table)
        a_switch.permanent_cover = {a_switch.section_my_loop: a_switch.id, a_switch.section_other_loop: a_switch.id}
        a_switch.timers = [timer_other for _ in range(len(_switches))]
        a_switch.timers[a_switch.id] = my_timer
        a_switch.defects = [[False, False] for _ in range(len(_switches))]
    for a_switch in _switches:
        a_switch.table = routing.dijkstra_route(a_switch, a_switch.permanent_table, a_switch.permanent_cover)
        # FINAL
        a_switch.permanent_table = a_switch.table

        # anomalies des switches : [boucle presente, boucle aiguillee] True ==> anomalies


def update():
    """
     fonction qui est lancée à chaque tour pour actualiser les états des switchs et leur table (pour le routage)
        :return: (void) modifications des éléments, attributs des switches
    """
    for s in _switches:
        # if s.is_routing_to_loop:
        info = routing.update_switch(s)
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


def cost_between(element1, element2):
    if type(element1) is Switch:
        if type(element2) is not Switch:
            if element2.loop is element1.my_loop or element2.loop is element1.other_loop:
                return element2.loop.distance_between(element1, element2)
        else:
            if element1.my_loop is element2.my_loop or element1.my_loop is element2.other_loop:
                return element1.my_loop.distance_between(element1, element2)
            elif element1.other_loop is element2.my_loop or element1.other_loop is element2.other_loop:
                return element1.other_loop.distance_between(element1, element2)
        switch = element1
        cost = 0
    else:
        # aller au premier switch sur boucle1
        boucle1 = element1.loop
        cost = float('inf')
        switch = None
        for cand_switch in boucle1.switches:
            d = boucle1.distance_between(element1, cand_switch)
            if d < cost:
                switch = cand_switch
                cost = d
    # ajout du cout de routage jusqu'à la boucle2
    if type(element2) is Switch:
        cost += switch.table[element2.section_my_loop][1]
        last_switch = element2
    else:
        cost += switch.table[element2.section_loop][1]
        # trajet entre le switch in de fin et l'élément2
        boucle2 = element2.loop
        last_switch = switch.table[element2.section_loop][2][len(switch.table[element2.section_loop][2]) - 2]
        last_switch = model_switch.get_switch_by_id(last_switch)
        cost += boucle2.distance_between(last_switch, element2)
    return cost


def get_switch_by_id(id):
    for s in _switches:
        if s.id == id:
            return s
    return None