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

        self.graph = Graph()
        self.rules = []
        self.congestions = [[False for j in range(self.graph.size)] for i in range(self.graph.size)]

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
        if self.graph.update_weight(previous_switch, current_switch, self.timers[capsule.id]):
            print("CONGESTION")
            new_rules = self.update_rules()
            self.congestions[self.graph.get_node_from_switch(previous_switch).id][self.graph.get_node_from_switch(current_switch).id] = True
        elif self.congestions[self.graph.get_node_from_switch(previous_switch).id][self.graph.get_node_from_switch(current_switch).id] == True and self.graph.no_more_congestion(previous_switch, current_switch, self.timers[capsule.id]):
            self.congestions[self.graph.get_node_from_switch(previous_switch).id][self.graph.get_node_from_switch(current_switch).id] = False

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
        def create_rules(station):
            end_node = self.graph.get_node_from_switch(station)
            unvisited_nodes = self.graph.get_switches_nodes().copy()

            while(len(unvisited_nodes)>0):
                for node in unvisited_nodes:
                    node_list = self.graph.calcul(node, end_node)
                    for i in range(1,len(node_list)):
                        if unvisited_nodes.count(node_list[i]) > 0:
                            change = node_list[i].loop.id != node_list[i-1].loop.id
                            self.rules.append(Rule(node_list[i].switch.id, node_list[i].loop.id, station, None, None, change))
                            unvisited_nodes.remove(node_list[i])

        for warehouse in self.warehouses:
            create_rules(warehouse)

        for station in self.stations:
            create_rules(station)


    def update_rules(self):
        new_rules = []

        def create_rules(station):
            end_node = self.graph.get_node_from_switch(station)
            unvisited_nodes = self.graph.get_switches_nodes().copy()

            while(len(unvisited_nodes)>0):
                for node in unvisited_nodes:
                    node_list = self.graph.calcul(node, end_node)
                    for i in range(1,len(node_list)):
                        if unvisited_nodes.count(node_list[i]) > 0:
                            change = node_list[i].loop.id != node_list[i-1].loop.id
                            new_rules.append(Rule(node_list[i].switch.id, node_list[i].loop.id, station, None, None, change))
                            unvisited_nodes.remove(node_list[i])

        for warehouse in self.warehouses:
            create_rules(warehouse)

        for station in self.stations:
            create_rules(station)
        self.rules= new_rule.copy()
        self.send_all_rules()
        return new_rules

    def send_all_rules(self):
        for rule in self.rules:
            for switch in self.switches:
                switch.add_rule(rule)

    def drain(self,destination):
        """
        Décharge une station qui en effectue la demande
        :param destination: Station qui effectue la dema
                end_node = self.graph.get_node_from_switch(station)
                unvisited_nodes = self.graph.get_switches_nodes().copy()

                while(len(unvisited_nodes)>0):
                    for node in unvisited_nodes:
                        node_list = self.graph.calcul(node, end_node)nde OBLIGATOIRE
        """
        destination.drain(warehouse.which_warehouse_after(destination))

    def refill(self,prio, destination, nb_to_send=1):
        """
        Réapprovisionne une station qui en effectue la demande
        :param prio: Priorité de la demande (10 si critique) OBLIGATOIRE
        :param destination: Station qui effectue la demande OBLIGATOIRE
        :param nb_to_send: Nombre de capsule vide à envoyer à la station
        """
        if prio == 10:
            test = False
            for capsule_t in capsule.get_capsules():
                if len(capsule_t.travelers)==0 and capsule_t.priority <= 6:
                    test = True
                    trajet = self.graph.calcul(self.graph.get_node_from_switch(capsule_t.next_element), self.graph.get_node_from_switch(destination))
                    for i in range(len(trajet)-1):
                        r = Rule(trajet[i].switch.id, trajet[i+1].loop.id, priority=6, empty=True, change=self.graph.change(trajet[i], trajet[i+1]))
                        self.rules.append(r)
                        self.send_all_rules()
                if test==True:
                    break;
            if test:
                test_warehouse = warehouse.which_warehouse_before(destination)
                if test_warehouse.capsule_queue.qsize()>0:
                    test_warehouse.send_capsule(destination, prio)

            else:
                test_warehouse = warehouse.which_warehouse_before(destination)
                if test_warehouse.capsule_queue.qsize()>1:
                    test_warehouse.send_capsule(destination, prio)

        else:
            test_warehouse = warehouse.which_warehouse_before(destination)
            if test_warehouse.capsule_queue.qsize()>0:
                    test_warehouse.send_capsule(destination, prio)
        print("LA")

    def temps_moy_stat(self,id,temps):
        test=True
        for i in self.tab_depart:
            if i[0]==id:
                test=False
                self.tab_temps.append(temps-i[1])
        if test :
            self.tab_depart.append([id,temps])

    def temps_moy_voy_stat(self,id,temps):
        test=True
        for i in self.tab_depart_voy:
            if i[0]==id:
                test=False
                self.tab_temps_voy.append(temps-i[1])
                self.tab_depart_voy.remove(i)
        if test :
            self.tab_depart_voy.append([id,temps])

    def temps_moy_voy(self):
        moy = 0
        j=0
        for i in self.tab_temps_voy:
            j+=1
            moy += i
        return moy/j

    def temps_moy(self):
        moy = 0
        j=0
        for i in self.tab_temps:
            j+=1
            moy += i
        return moy/j





def get_controller():
    return _controller
