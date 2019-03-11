from settings import simlog
from stats import stats_array as sa, stats_average_array as saa

class StatsRecorder:
  """
  Classe qui centralise la collecte des statistiques lors d'une simulation
  """
  def __init__(self, tick=0):
    """
    constructeur du StatsRecorder
    """
    self._init_tick = tick
    self._stopping_tick = -1
    self._is_recording = False
    # loop
    self._exiting_loop = sa.StatsArray("Nombre de capsules quittant une boucle.")
    self._joining_loop = sa.StatsArray("Nombre de capsules rejoingnant une boucle.")
    self._capsule_average_loop = saa.StatsAverageArray("Nombre de capsules moyen par boucle.")
    # drain
    self._sent_capsules_drain = saa.StatsAverageArray("Nombre de capsules émises moyen par drainage.")
    self._called_capsules_drain = saa.StatsAverageArray("Nombre de capsules rappelées moyen par drainage.")
    # traveler
    self._waiting_time_traveler = saa.StatsAverageArray("Temps d'attente moyen d'un voyageur.", "secs")
    self._traveling_time_traveler = saa.StatsAverageArray("Temps de trajet moyen d'un voyageur.", "secs")
    # station
    self._stopped_capsules_station = saa.StatsAverageArray("Nombre de capsules arrêtées moyen d'une station.")
    self._departure_from_station = saa.StatsAverageArray("Nombre de départs de capsule moyen d'une station.")
    self._arrival_to_station = saa.StatsAverageArray("Nombre d’arrivées de capsule moyen d'une station.")
    self._waiting_travelers = saa.StatsAverageArray("Nombre de voyageurs moyen dans la file d’attente d'une station.")
    # capsule
    self._busy_moving_time = saa.StatsAverageArray("Temps « occupée et mobile » moyen d'une capsule.", "secs")
    self._busy_not_moving_time = saa.StatsAverageArray("Temps « occupée et immobile » moyen d'une capsule.", "secs")
    self._free_not_moving_time = saa.StatsAverageArray("Temps « libre et immobile » moyen d'une capsule", "secs")
    self._free_moving_time = saa.StatsAverageArray("Temps « libre et mobile » moyen d'une capsule", "secs")
    self._time_in_network = saa.StatsAverageArray("Temps sur le circuit moyen d'une capsule.", "secs")
    self._time_in_warehouse = saa.StatsAverageArray("Temps dans un entrepôt moyen d'une capsule.", "secs")
    self._traveling_distance = saa.StatsAverageArray("Distance de trajet moyenne d'une capsule.", "secs")
    # record
    self._start_listen(self._init_tick)
    
  def _start_listen(self, tick):
    """
    à partir de cet appel, l'objet va enregistrer les informations qu'on lui envoie
    """
    self._starting_tick = tick
    self._is_recording = True
    simlog.info("StatsRecorder is now on.")

  def stop_listen(self, tick):
    """
    à partir de cet appel, l'objet va arrêter d'enregistrer les informations qu'on lui envoie
    """
    self._is_recording = False
    self._stopping_tick = tick
    simlog.info("StatsRecorder is now off.")

  def extract(self):
    simlog.info("Extracting stats.")
    buffer = "# loops stats\n\n"
    buffer += self._exiting_loop.extract()
    buffer += self._joining_loop.extract()
    buffer += self._capsule_average_loop.extract()
    buffer += "\n"
    stats_file = open("out/latest-stats.txt", "w")
    stats_file.write(buffer)
    stats_file.close()

  def get_running_time(self, tick):
    """
    renvoie le nombre de secondes depuis lequel le Recorder a été lancé
    """
    return tick - self._init_tick + 1

  def get_record_time(self):
    """
    renvoie le nombre de secondes pendant lequel le Recorder a enregistré
    """
    return self._stopping_tick - self._starting_tick + 1 if self._stopping_tick != -1 else -1

  # à propos des loops
  def add_exiting_loop(self, loop):
    """
    incremente le compteur de capsules quittant une boucle
    """
    if not self._is_recording:
      return
    self._exiting_loop.add(loop)

  def add_joining_loop(self, loop):
    """
    incremente le compteur de capsules rejoingnant une boucle
    """
    if not self._is_recording:
      return
    self._joining_loop.add(loop)
  
  def add_capsule_average_loop(self, quantity, loop):
    """
    ajoute le nombre de capsules d'une loop
    """
    if not self._is_recording:
      return
    self._capsule_average_loop.add(quantity, loop)

  # à propos du drainage
  def add_sent_capsules_drain(self, quantity, loop):
    """
    ajoute le nombre de capsules ayant quitté la loop
    """
    if not self._is_recording:
      return
    self._sent_capsules_drain.add(quantity, loop)

  def add_called_capsules_drain(self, quantity, loop):
    """
    ajoute le nombre de capsules étant entrées dans la loop
    """
    if not self._is_recording:
      return
    self._called_capsules_drain.add(quantity, loop)

  # à propos des travelers
  def add_waiting_time_traveler(self, quantity, loop):
    if not self._is_recording:
      return
    self._waiting_time_traveler.add(quantity, loop)
  
  def add_traveling_time_traveler(self, quantity, loop):
    if not self._is_recording:
      return
    self._traveling_time_traveler.add(quantity, loop)

  # à propos des stations
  def add_stopped_capsules_station(self, quantity, loop):
    if not self._is_recording:
      return
    self._stopped_capsules_station.add(quantity, loop)

  def add__departure_from_station(self, quantity, loop):
    if not self._is_recording:
      return
    self._departure_from_station.add(quantity, loop)

  def add_arrival_to_station(self, quantity, loop):
    if not self._is_recording:
      return
    self._arrival_to_station.add(quantity, loop)

  def add__arrival_to_station(self, quantity, loop):
    if not self._is_recording:
      return
    self._waiting_travelers.add(quantity, loop)

  # à propos des capsules
  def add_busy_moving_time(self, quantity, loop):
    if not self._is_recording:
      return
    self._busy_moving_time.add(quantity, loop)

  def add_busy_not_moving_time(self, quantity, loop):
    if not self._is_recording:
      return
    self._busy_not_moving_time.add(quantity, loop)

  def add_free_not_moving_time(self, quantity, loop):
    if not self._is_recording:
      return
    self._free_not_moving_time.add(quantity, loop)

  def add_free_moving_time(self, quantity, loop):
    if not self._is_recording:
      return
    self._free_moving_time.add(quantity, loop)

  def add_time_in_network(self, quantity, loop):
    if not self._is_recording:
      return
    self._time_in_network.add(quantity, loop)

  def add_time_in_warehouse(self, quantity, loop):
    if not self._is_recording:
      return
    self._time_in_warehouse.add(quantity, loop)

  def add_traveling_distance(self, quantity, loop):
    if not self._is_recording:
      return
    self._traveling_distance.add(quantity, loop)