



class Statistiques:

	def __init__(self):
		self._waiting_times = [] # tableau des temps d'attente
		self._nb_traveler = 0 # nombre actuel de voyageur dans une capsule
		self._traveling_pods = {} # tableau des capsules en voyage
		self._travels = [] # tableau des voyages effectués


	def add_traveling_pod(self,pod,departure_time,traveler):
		self._traveling_pods[pod.id] = [pod,departure_time,-1,traveler]
		if traveler:
			self._nb_traveler += 1
			print("number of traveler: " + str(self._nb_traveler))

	def remove_traveling_pod(self,pod,timestamp):
		self._traveling_pods[pod.id][2] = timestamp
		self.travels.append(self._traveling_pods[pod.id])
		self._traveling_pods[pod.id] = []
		if len(pod.travelers)>0:
			self._nb_traveler -= 1
			print("number of traveler: " + str(self._nb_traveler))

	def add_waiting_time(self,timestamp,waiting_time):
		self._waiting_times.append((timestamp,waiting_time))
		print(self._waiting_times)
