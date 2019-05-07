from model import capsule
from model import switch
from model import graph
from model.graph import Graph
from model.rule import *
from model import station
from model import warehouse

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
        self.graph = Graph()
        self.rules = []

        self.init_rules()
        self.send_all_rules()

    def update_from_switch(self, capsule):
        """
         fonction qui est lancée à chaque fois qu'une capsule passe un switch
         :param previous_switch : le dernier switch/station/warehouse parcouru
         :param current_switch : le switch qui a routé la capsule
         :param capsule : la capsule routée
        """
        previous_switch = capsule.current_element
        current_switch = capsule.next_element
        if self.graph.update_weights(previous_switch, current_switch, self.timers[capsule.id]):
            print("CONGESTION")

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

    def refill(self, prio, destination, nb_to_send=1):
        """
        Réapprovisionne une station qui en effectue la demande
        :param prio: Priorité de la demande (10 si critique) OBLIGATOIRE
        :param destination: Station qui effectue la demande OBLIGATOIRE
        :param nb_to_send: Nombre de capsule vide à envoyer à la station
        """

        if prio == 10:
            test = False
            for capsule in self.capsules:
                if capsule.travelers==list() and capsule.priority <= 6:
                    test = True
                    trajet = graph.calcul(self.get_next(capsule), destination)
                    for i in range(len(trajet)):
                        r = Rule(priority=6, empty=True, change=graph.change(trajet[i], trajet[i+1]))
                        trajet[i].add_rule(r)
            if test:
                warehouse = which_warehouse_before(destination)
                warehouse.send(Capsule(warehouse, destination), prio)
            else:
                warehouse = which_warehouse_before(destination)
                warehouse.send(Capsule(warehouse, destination), 1)
        else:
            warehouse = which_warehouse_before(destination)
            warehouse.send(Capsule(warehouse, destination), prio)

    def drain(self, destination):
        """
        Décharge une station qui en effectue la demande
        :param destination: Station qui effectue la demande OBLIGATOIRE
        """
        destination.drain(which_warehouse_after)

    def stop_timer(self, capsule):
        self.timers[capsule.id] = -1

    def init_rules(self):
        for warehouse in self.warehouses:
            end_node = self.graph.get_node_from_switch(warehouse)
            unvisited_nodes = self.graph.get_switches_nodes().copy()

            for node in unvisited_nodes:
                #beacoup de print pour test (à enlever quand ça marchera)
                print("debut")
                print(node.id)
                print(end_node.id)
                node_list = self.graph.calcul(node, end_node)
                for kkk in node_list:
                    print(kkk.id)
                print("fin")

                for i in range(len(node_list)-1):
                    if unvisited_nodes.count(node_list[i]) > 0:
                        change = node_list[i].loop.id != node_list[i+1].loop.id
                        self.rules.append(Rule(node.switch.id, node.loop.id, warehouse, None, change))
                        unvisited_nodes.remove(node_list[i])

        for station in self.stations:
            end_node = self.graph.get_node_from_switch(station)
            unvisited_nodes = self.graph.get_switches_nodes().copy()

            for node in unvisited_nodes:
                node_list = self.graph.calcul(node, end_node)
                for i in range(len(node_list)-1):
                    if unvisited_nodes.count(node_list[i]) > 0:
                        change = node_list[i].loop.id != node_list[i+1].loop.id
                        self.rules.append(Rule(node.switch.id, node.loop.id, station, None, change))
                        unvisited_nodes.remove(node_list[i])

    def send_all_rules(self):
        for rule in self.rules:
            for switch in self.switches:
                switch.add_rule(rule)

def get_controller():
    return _controller
