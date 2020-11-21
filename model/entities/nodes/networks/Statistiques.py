import statistics as s
import os, shutil, glob

"""Classe permettant d'effectuer des statistiques sur les simulations"""

class Statistiques:

	def __init__(self):
		self._waiting_times = []  		# tableau des temps d'attente
		self._waiting_time = 0
		self._average_waiting_time = 0
		self._travel_times_since_last_minute = []
		self._travel_times = []
		self._average_travel_time = 0
		self._nb_traveler = 0  			# nombre actuel de voyageur dans une capsule
		self._waiting_travelers = {}    # dictionnaire des voyageurs en attente
		self._nb_pod = 0
		self._traveling_pods = {}  		# dictionnaire des capsules en voyage
		# self._travels = []  			# tableau des voyages effectués
		self._total_generated_travelers = 0
		# Gestion fichiers 
		self.delete_old_images_and_csv_files()
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
		self._travel_times_since_last_minute.append(timestamp - departure_time)
		self._travel_times.append(timestamp - departure_time)
		self._average_travel_time = round(s.mean(self._travel_times), 2)

	def get_travel_times_since_last_minute_and_reset(self):
		arr = self._travel_times_since_last_minute
		self._travel_times_since_last_minute = []
		return arr


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

		# Ecriture stats globales
		csvfile = open('stats/global/stat_log.csv', 'a')
		csvfile.write(row)
		csvfile.close()


	def write_columns_names_for_all_stations(self, stations):
		for station in stations:
			self.write_columns_names_for_station(station)


	def write_stats_for_all_stations(self, time, stations):
		globalWaitingTimeCsv = open("stats/global/globalWaitingTime/globalWaitingTime.csv", 'a')
		globalWaitingTimeCsv.write(time + ",")
		#autre fichier csv global    A METTRE

		# Ecriture stats pour chaque station
		for station in stations:
			self.write_stats_for_station(time, station, globalWaitingTimeCsv)
		globalWaitingTimeCsv.write("\n")
		globalWaitingTimeCsv.close()


	def write_columns_names_for_station(self, station):
		folderPath = "stats/stations/" + station.name
		access_rights = 0o755
		try:
			os.mkdir(folderPath, access_rights)
		except OSError:
			print ("Creation of the directory %s failed" % folderPath)
		filename = 'stats/stations/' + station.name + "/stats.csv"
		csvfile = open(filename, 'a')
		csvfile.write("Time, Waiting duration (in s)\n")
		csvfile.close()	


	def create_global_directories(self):
		self.create_directory("stats/global/globalWaitingTime")
		self.create_directory("stats/global/globalTravelTime")
		self.create_directory("stats/global/failedInsertions")

		self.create_directory("stats/global/travelersInAPod")
		self.create_directory("stats/global/waitingTravelers")
		self.create_directory("stats/global/travelingPods")

	def create_directory(self, filename):
		access_rights = 0o755
		try:
			os.mkdir(filename, access_rights)
		except OSError:
			print ("Creation of the directory %s failed" % filename)
			

	def write_stats_for_station(self, time, station, globalWaitingTimeCsv):
		filename = 'stats/stations/' + station.name + "/stats.csv"
		csvStationFile = open(filename, 'a')
		csvStationFile.write(time + ",")

		arr_waiting_times_since_last_minute = station.get_waiting_times_since_last_minute_and_reset()
		csvStationFile.write(self.array_to_proper_string_for_csv(arr_waiting_times_since_last_minute) + "\n")
		globalWaitingTimeCsv.write(self.array_to_proper_string_for_csv(arr_waiting_times_since_last_minute) + ",")

		csvStationFile.close()

	
	def write_stats_insertion(self, time, switches):
		failedInsertionCsv = open("stats/global/failedInsertions/failedInsertions.csv", 'a')

		row = str(time) + ","
		failedInsertion = 0
		for switch in switches:
			if (type(switch).__name__ == "SwitchOut"):
				failedInsertion += switch.get_failed_insertion_since_last_minute_and_reset()

		row += str(failedInsertion)
		row += "\n"

		failedInsertionCsv.write(row)
		failedInsertionCsv.close()


	def write_travel_time_global(self, time):
		globalTravelTimeCsv = open("stats/global/globalTravelTime/globalTravelTime.csv", 'a')

		row = str(time) + ","
		for travel_time in self.get_travel_times_since_last_minute_and_reset():
			row += str(travel_time) + ","
		row = row[:-1]	# On enleve la derniere virgule
		row += "\n"

		globalTravelTimeCsv.write(row)
		globalTravelTimeCsv.close()


	def array_to_proper_string_for_csv(self, array):	# array = [2, 5, 8.2]
		proper_string_for_csv = ""
		if (len(array) == 0):
			return ""
		else:
			proper_string_for_csv += str(array[0])
			for value in array:
				proper_string_for_csv += "|"
				proper_string_for_csv += str(value)
			return proper_string_for_csv				# proper_string_for_csv = 2|5|8.2




	def delete_old_images_and_csv_files(self):
		files = glob.glob('stats/global/*')
		for f in files:
			if (os.path.isdir(f)):
				filesInDirectory = glob.glob(f + "/*")
				for fileInDirectory in filesInDirectory:
					os.remove(fileInDirectory)
			elif (f != "stats/global/infos.txt"):		# si un fichier et pas un dossier
				os.remove(f)
				
		files = glob.glob('stats/stations/*')
		#print(files)
		#print("\n\n")
		for f in files:
			#print(f)
			if (os.path.isdir(f)):

				# On supprime les fichiers dans le dossier
				filesInDirectory = glob.glob(f + "/*")
				for fileInDirectory in filesInDirectory:
					#print(fileInDirectory)
					os.remove(fileInDirectory)

				# On supprime maintenant le dossier
				try:
					os.rmdir(f)
				except OSError:
					print ("Deletion of the directory " + f + " failed")
					
			else:		# fichier
				if (f != "stats/stations/infos.txt"):
					os.remove(f)
		

	def traveling_pods(self):
		""" Renvoie les pods en mouvement du reseau
		Appele par la fonction get_pod_of_user de network
		"""
		return self._traveling_pods
