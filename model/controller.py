from model import capsule
from model import switch
from model import graph


_controller = None


class Controller:
	def __init__(self):
		global _controller
		self.capsules = capsule.get_capsules()
		self.switches = switch.get_switches()
		self.timers = []
		self.graph = Graph()

	def update_from_switch(self, switch, rule, capsule):
	"""
     fonction qui est lancée à chaque fois qu'une capsule passe un switch
     :param switch : le switch qui a routé la capsule
     :param rule : la règle utilisée par le routeur pour router la capsule
     :param capsule : la capsule routée
    """
		if rule.change:
			loop = switch.loop
		else:
			loop = switch.next_loop

		graph.update_weights(loop, self.timers[capsule.id])

		self.timers[capsule.id] = 0


	def update(self):
		"""
	     fonction qui est lancée à chaque tour pour actualiser les timers du controller
	     /!\à compléter avec les vraies valeurs
	    """
	    for i in range(len(self.timers)):
	    	timers[i] += 1

	    	if timers[i] >= 1000:
	    		disable_way(this.capsules[i].loop)

def disable_way(loop):
"""
 fonction qui est lancée quand une boucle est coupée
 met à jour le poids de la boucle à +infini dans le graph
"""
	graph.disable_way(loop)
