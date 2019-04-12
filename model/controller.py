from model import capsule
from model import switch
from model import graph
from model.capsule import Capsule
from model.graph import Graph
from model.rule import *
from model import station
from model.warehouse import which_warehouse_before

_controller = None


class Controller:

	def __init__(self):
        global _controller
        _controller = self
		self.capsules = capsule.get_capsules()
		self.switches = switch.get_switches()
		self.timers = [-1] * len(capsules)
		self.graph = Graph()

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
            if timers[i] != -1:
    	    	timers[i] += 1
    	    	next_switch = self.capsules[i].next_element
    	    	previous_switch = self.capsules[i].current_element

    	    	if timers[i] >= self.graph.get_time_max(previous_switch, next_switch):
    	    		self.graph.disable_way(previous_switch, next_switch)

	def refill(self, prio, destination, nb_to_send=1):
		if prio == 1:
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

    def stop_timer(self, capsule):
        self.timers[capsule.id] = -1

def get_controller():
    return _controller
