from model import capsule
from model import switch
from model.graph import Graph
from model.rule import *
from model import station
from model import warehouse
from model import node

_controller = None


class Controller:

    def __init__(self):
        global _controller
        _controller = self
        self.capsules = capsule.get_capsules()
        self.switches = switch.get_switches()
        self.warehouses = warehouse.get_warehouses()
        self.stations = station.get_stations()
        self.timers = [-1] * len(self.capsules)
        self.tab_depart = []
        self.tab_temps = []
        self.tab_depart_voy = []
        self.tab_temps_voy = []

        self.graph = Graph(self.warehouses, self.stations, self.switches)
        self.rules = []
        self.congestions = [[False for j in range(self.graph.size)] for i in range(self.graph.size)]

        self.init_rules()
        self.send_all_rules()

    def update_from_switch(self, capsule):
        """
         fonction qui est lancée à chaque fois qu'une capsule passe un switch
         :param capsule : la capsule routée
        """
        previous_switch = capsule.current_element  # last node browsed
        current_switch = capsule.next_element  # switch which route the pod
        previous_node = self.graph.get_node_from_elt(previous_switch)
        current_node = self.graph.get_node_from_elt(current_switch)
        if self.graph.update_weight(previous_switch, current_switch, self.timers[capsule.id]):
            print("CONGESTION")
            new_rules = self.update_rules()
            self.replace_rules(new_rules)
            self.congestions[previous_node.id][current_node.id] = True
        elif self.congestions[previous_node.id][current_node.id] and self.graph.no_more_congestion(previous_switch, current_switch, self.timers[capsule.id]):
            self.congestions[previous_node.id][current_node.id] = False
        self.timers[capsule.id] = 0

    def update(self):
        """
         fonction qui est lancée à chaque tour pour actualiser les timers du controller
        """
        for i in range(len(self.timers)):
            if self.timers[i] != -1:
                self.timers[i] += 1
                next_switch = self.capsules[i].next_element
                previous_switch = self.capsules[i].current_element

                if self.timers[i] >= self.graph.get_time_max(previous_switch, next_switch):
                    self.graph.disable_way(previous_switch, next_switch)

    def stop_timer(self, capsule):
        self.timers[capsule.id] = -1

    def init_rules(self):
        def create_rules(elt):
            end_node = self.graph.get_node_from_elt(elt)  # noeud correspondant à l'élément station
            unvisited_nodes = self.graph.get_switches_nodes().copy()  # copie de tous les switchs
            while len(unvisited_nodes) > 0:  # Tant qu'on a des switchs non visités
                for node_switch in unvisited_nodes:
                    chemin = self.graph.calcul(node_switch, end_node)  # Calcul du plus court chemin entre le switch et end_node
                    for i in range(1, len(chemin)):
                        if unvisited_nodes.count(chemin[i]) > 0: # Si on a pas encore visité un noeud du chemin on lui associe une règle
                            change_loop = chemin[i].loop.id != chemin[i - 1].loop.id # On regarde si on a changé de boucle
                            regle = Rule(chemin[i].elt.id, chemin[i].loop.id, elt, None, None, change_loop)
                            self.rules.append(regle)
                            unvisited_nodes.remove(chemin[i])

        # On créé des règle entre les switch et les garages/stations

        for warehouse in self.warehouses:
            create_rules(warehouse)

        for station in self.stations:
            create_rules(station)

    def update_rules(self):
        new_rules = []

        def create_rules(station):
            end_node = self.graph.get_node_from_elt(station)
            unvisited_nodes = self.graph.get_switches_nodes().copy()

            while len(unvisited_nodes) > 0:
                for node in unvisited_nodes:
                    node_list = self.graph.calcul(node, end_node)
                    for i in range(1, len(node_list)):
                        if unvisited_nodes.count(node_list[i]) > 0:
                            change = node_list[i].loop.id != node_list[i - 1].loop.id
                            new_rules.append(
                                Rule(node_list[i].elt.id, node_list[i].loop.id, station, None, None, change))
                            unvisited_nodes.remove(node_list[i])

        for warehouse in self.warehouses:
            create_rules(warehouse)

        for station in self.stations:
            create_rules(station)
        return new_rules

    def send_all_rules(self):
        for rule in self.rules:
            for switch in self.switches:
                switch.add_rule(rule)

    def replace_rules(self, r):
        for rule in self.rules:
            if rule.priority is None:
                for switch in self.switches:
                    switch.remove_rule(rule)
                self.rules.remove(rule)
        for rule in r:
            if self.rules.count(rule) == 0:
                self.rules.append(rule)
                for switch in self.switches:
                    switch.add_rule(rule)

    def send_list_rules(self, r):
        for rule in r:
            if self.rules.count(rule) == 0:
                self.rules.append(rule)
                for switch in self.switches:
                    switch.add_rule(rule)

    def drain(self, destination):
        """
        Décharge une station qui en effectue la demande
        :param destination: Station qui effectue la dema
                end_node = self.graph.get_node_from_elt(station)
                unvisited_nodes = self.graph.get_switches_nodes().copy()

                while(len(unvisited_nodes)>0):
                    for node in unvisited_nodes:
                        node_list = self.graph.calcul(node, end_node)nde OBLIGATOIRE
        """
        destination.drain(warehouse.which_warehouse_after(destination))

    def refill(self, prio, destination, nb_to_send=1):
        """
        Réapprovisionne une station qui en effectue la demande
        :param prio: Priorité de la demande (10 si critique) OBLIGATOIRE
        :param destination: Station qui effectue la demande OBLIGATOIRE
        :param nb_to_send: Nombre de capsule vide à envoyer à la station
        """
        if prio == 10:
            test = False
            for capsule_t in capsule.get_empty_capsules():
                if len(capsule_t.travelers) == 0 and capsule_t.priority <= 6:
                    test = True
                    trajet = self.graph.calcul(self.graph.get_node_from_elt(capsule_t.next_element),
                                               self.graph.get_node_from_elt(destination))
                    for i in range(len(trajet) - 1):
                        new_rules = list()
                        r = Rule(trajet[i].elt.id, trajet[i + 1].loop.id, priority=6, empty=True,
                                 change=self.graph.change(trajet[i], trajet[i + 1]))
                        new_rules.append(r)
                        self.send_list_rules(new_rules)
                if test:
                    break
            if test:
                test_warehouse = warehouse.which_warehouse_before(destination)
                if test_warehouse.capsule_queue.qsize() > 0:
                    test_warehouse.drain(destination, prio)

            else:
                test_warehouse = warehouse.which_warehouse_before(destination)
                if test_warehouse.capsule_queue.qsize() > 1:
                    test_warehouse.drain(destination, prio)

        else:
            test_warehouse = warehouse.which_warehouse_before(destination)
            if test_warehouse.capsule_queue.qsize() > 0:
                test_warehouse.drain(destination, prio)

    def disable_way(self, id1, id2):
        self.graph.delete_section(id1, id2)
        new_rules = self.update_rules()
        self.replace_rules(new_rules)
        print("COUPURE D'UNE VOIE")

    """
    Les 4 fonctions suivantes sont des fonctions permettant de retourner des statistiques sur le temps
    moyen d'attentes des voyageurs (temps_moy_voy_stat/temps_moy_voy()
    et sur le temps moyen de trajet des capsules (temps_moy_stat/temps_moy)
    Dans la pratique on créé des tableaux intermédiares mis à jour lors de l'arrivée/départ des capsules ou des voyageurs
    Puis on calcule la moyenne.
    """
    def temps_moy_stat(self,id,temps):
        test=True
        for i in self.tab_depart:
            if i[0] == id:
                test = False
                self.tab_temps.append(temps - i[1])
                i[0] = -1
        if test:
            self.tab_depart.append([id, temps])

    def temps_moy_voy_stat(self, id, temps):
        test = True
        for i in self.tab_depart_voy:
            if i[0] == id:
                test = False
                self.tab_temps_voy.append(temps - i[1])
                i[0] = -1
        if test:
            self.tab_depart_voy.append([id, temps])

    def temps_moy_voy(self):
        moy = 0
        j = 0
        for i in self.tab_temps_voy:
            j += 1
            moy += i
        if j == 0:
            return (0)
        else:
            return moy / j

    def temps_moy(self):
        moy = 0
        j = 0
        for i in self.tab_temps:
            j += 1
            moy += i
        if j == 0:
            return (0)
        else:
            return moy / j


def get_controller():
    return _controller
