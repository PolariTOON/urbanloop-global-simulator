from model import capsule
from model import switch
from model import graph

class Controller:
	def __init__(self):
		self.capsules = capsule.get_capsules()
		self.switches = switch.get_switches()
		self.timers = []
		self.graph = Graph()

	def update_from_switch(self, switch, capsule):
	"""
     fonction qui est lancée à chaque fois qu'une capsule passe un switch
     :param switch : le switch qui a routé la capsule
     :param capsule : la capsule routée
    """
		self.graph.update_weights(switch.uuid, self.timers[capsule.id])

		self.timers[capsule.id] = 0


	def update(self):
		"""
	     fonction qui est lancée à chaque tour pour actualiser les timers du controller
	    """
	    for i in range(len(self.timers)):
	    	timers[i] += 1
	    	next_switch = self.capsules[i].next_element.uuid
	    	previous_switch = self.capsules[i].current_element.uuid

	    	if timers[i] >= self.graph.matrix[previous_switch][next_element]*10:
	    		disable_way(previous_switch, next_switch)

def disable_way(previous_switch, next_switch):
"""
 fonction qui est lancée quand une boucle est coupée
 met à jour le poids de la boucle à +infini dans le graph
"""
	graph.disable_way(previous_switch, next_switch)
