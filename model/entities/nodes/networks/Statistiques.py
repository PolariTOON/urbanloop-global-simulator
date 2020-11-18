import statistics as s

"""Classe permettant d'effectuer des statistiques sur les simulations"""

class Statistiques:

	def __init__(self):
		self._waiting_times = []  		# tableau des temps d'attente
		self._waiting_time = 0
		self._average_waiting_time = 0
		self._travel_times = []
		self._average_travel_time = 0
		self._nb_traveler = 0  			# nombre actuel de voyageur dans une capsule
		self._waiting_travelers = {}    # dictionnaire des voyageurs en attente
		self._nb_pod = 0
		self._traveling_pods = {}  		# dictionnaire des capsules en voyage
		# self._travels = []  			# tableau des voyages effectués
		self._total_generated_travelers = 0
		csvfile = open('stats/global/stat_log.csv', 'w')
		csvfile.write('Time, total travelers, travelers in a pod, waiting travelers, traveling pods, average waiting time, average travel time, total generated travelers\n')
		csvfile.close()

	def add_traveling_pod(self, pod, departure_time, traveler, origin):
		"""fonction pour compter le nombre de pods en circulation et le nombre de voyageurs en transit"""
		self._traveling_pods[pod.id] = [pod, departure_time, -1, traveler]
		self._nb_pod += 1
		if traveler:
			self._nb_traveler += 1
			self._waiting_travelers[origin] -= 1
			# print("\u001B[32m", "\t>", "number of traveler: " + str(self._nb_traveler), "\u001B[0m")

	def remove_traveling_pod(self, pod, timestamp):
		"""fonction qui compte lorsqu'un pod arrête de circuler"""
		if not pod.id in self._traveling_pods.keys():
			print("\u001B[31m", "\t\tclef introuvable", pod.id, "(Statistiques l.23)", "\u001B[0m")  # todo recharger les pods ici quand on charge un fichier en cours de simulation
		else:
			# self._traveling_pods[pod.id][2] = timestamp
			# self._travels.append(self._traveling_pods[pod.id])
			if self._traveling_pods[pod.id][3]:
				self._nb_traveler -= 1
				self.add_travel_time(timestamp,self._traveling_pods[pod.id][1])
				# print("\u001B[31m", "\t> number of traveler: " + str(self._nb_traveler), "\u001B[0m")
			self._traveling_pods[pod.id] = []
			self._nb_pod -= 1

	def add_waiting_time(self, timestamp, waiting_time):
		"""fonction de calcul du temps d'attente moyen des voyageurs"""
		self._waiting_times.append(waiting_time)
		self._waiting_time = waiting_time
		self._average_waiting_time = round(s.mean(self._waiting_times), 2)
		# print(self._waiting_times)

	def add_travel_time(self, timestamp, departure_time):
		self._travel_times.append(timestamp - departure_time)
		self._average_travel_time = round(s.mean(self._travel_times), 2)

	def add_waiting_traveler(self, station):
		"""ajout d'un voyageur en attente"""
		if station not in self._waiting_travelers.keys():
			self._waiting_travelers[station] = 0
		self._waiting_travelers[station] += 1
		self._total_generated_travelers += 1
	
	def serialize(self):
		dict = {
		"waiting_times": self._waiting_times,
		"waiting_time": self._average_waiting_time,
		"nb_pod": self._nb_pod,
		"nb_traveler": self._nb_traveler
		}

		return dict

	def print_stats(self):
		waiting_travelers = 0
		for key in self._waiting_travelers.keys():
			waiting_travelers += self._waiting_travelers[key]
		print("\t\t\t\t\u001B[34m|\u001B[0m nb of travelers      = ", waiting_travelers + self._nb_traveler)
		print("\t\t\t\t\u001B[34m|\u001B[0m travelers in a pod   = ", self._nb_traveler)
		print("\t\t\t\t\u001B[34m|\u001B[0m waiting travelers        = ", self._waiting_travelers)
		print("\t\t\t\t\u001B[34m|\u001B[0m cumul. waiting travelers = ", waiting_travelers)
		print("\t\t\t\t\u001B[34m|\u001B[0m traveling pods           = ", self._nb_pod)
		print("\t\t\t\t\u001B[34m|\u001B[0m average waiting time     = ", self._average_waiting_time, "s")

	def write_stats_line(self, time):
		waiting_travelers = 0
		for key in self._waiting_travelers.keys():
			waiting_travelers += self._waiting_travelers[key]
		total_travelers = waiting_travelers + self._nb_traveler

		row = time + ","
		row += str(total_travelers) + ","
		row += str(self._nb_traveler) + ","
		row += str(waiting_travelers) + ","
		row += str(self._nb_pod) + ","
		row += str(self._average_waiting_time) + ","
		row += str(self._average_travel_time) + ","
		row += str(self._total_generated_travelers) + "\n"

		csvfile = open('stat_log.csv', 'a')
		csvfile.write(row)
		csvfile.close()


	def traveling_pods(self):
		""" Renvoie les pods en mouvement du reseau
		Appele par la fonction get_pod_of_user de network
		"""
		return self._traveling_pods
