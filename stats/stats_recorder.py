from settings import simlog
from stats import StatsTickArray

class StatsRecorder:
  """
  Classe qui centralise la collecte des statistiques lors d'une simulation
  """
  def __init__(self, tick=0):
    """
    constructeur du StatsRecorder
    """
    self.init_tick = tick
    # loop
    self.exiting_loop = StatsArray("Nombre de capsules quittant une boucle.")
    self.joining_loop = StatsArray("Nombre de capsules rejoingnant une boucle.")
    self.capsule_average_loop = StatsAverageArray("Nombre de capsules moyen par boucle.")
    
  def start_listen(self, tick):
    """
    à partir de cet appel, l'objet va enregistrer les informations qu'on lui envoie
    """
    self.starting_tick = tick
    self.is_listening = True
    simlog.info("StatsRecorder is now on.")

  def stop_listen(self, tick):
    """
    à partir de cet appel, l'objet va arrêter d'enregistrer les informations qu'on lui envoie
    """
    self.stopping_tick = tick
    self.is_listening = False
    simlog.info("StatsRecorder is now off.")
  
  # à propos des loops
  def add_exiting_loop(self, tick, loop):
    """
    incremente le compteur de capsules quittant une boucle
    """
    self.exiting_loop.add(tick, loop)

  def add_exiting_loop(self, tick, loop):
    """
    incremente le compteur de capsules rejoingnant une boucle
    """
    self.joining_loop.add(tick, loop)
  
  def add_capsule_average_loop(self, quantity, loop, tick):
    """
    ajoute le nombre de capsules d'une loop
    """
    self.capsule_average_loop.add(tick, loop)