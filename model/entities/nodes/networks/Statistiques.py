import statistics as s

class Statistiques:

	def __init__(self):
		self._waiting_times = []  		# tableau des temps d'attente
		self._waiting_time = 0
		self._average_waiting_time = 0
		self._nb_traveler = 0  			# nombre actuel de voyageur dans une capsule
		self._nb_pod = 0
		self._traveling_pods = {}  		# dictionnaire des capsules en voyage
		self._travels = []  			# tableau des voyages effectués

	def add_traveling_pod(self, pod, departure_time, traveler):
		self._traveling_pods[pod.id] = [pod, departure_time, -1, traveler]
		self._nb_pod += 1
		if traveler:
			self._nb_traveler += 1
			# print("\u001B[32m", "\t>", "number of traveler: " + str(self._nb_traveler), "\u001B[0m")

	def remove_traveling_pod(self, pod, timestamp):
		if not pod.id in self._traveling_pods.keys():
			print("\u001B[31m", "\t\tclef introuvable", pod.id, "(Statistiques l.23)", "\u001B[0m")  # todo recharger les pods ici quand on charge un fichier en cours de simulation
		else:
			self._traveling_pods[pod.id][2] = timestamp
			self._travels.append(self._traveling_pods[pod.id])
			self._traveling_pods[pod.id] = []
			self._nb_pod -= 1  # todo revoir le compte de voyageurs
			self._nb_traveler -= 1
			# print("\u001B[31m", "\t> number of traveler: " + str(self._nb_traveler), "\u001B[0m")

	def add_waiting_time(self, timestamp, waiting_time):
		self._waiting_times.append(waiting_time)
		self._waiting_time = waiting_time
		self._average_waiting_time = round(s.mean(self._waiting_times),2)
		# print(self._waiting_times)
	
	def serialize(self):
		dict = {
		"waiting_times": self._waiting_times,
		"waiting_time": self._average_waiting_time,
		"nb_pod": self._nb_pod,
		"nb_traveler": self._nb_traveler
		}

		return dict

