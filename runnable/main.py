import time

from settings import network
from settings import simlog
from simulator import sim_loop
from simulator.traveler_generator import total_generated

"""Fichier principal du projet -- absence d'interface graphique """

"""Initialisation"""
START_TIME = time.time()
starting_sim_loop = sim_loop.SimLoop()

network.load() # chargement du réseau

"""Start"""
if __name__ == "__main__":
    simlog.debug("Simulation starts")
    sim_loop.run_simulation(sim_loop=starting_sim_loop)
    simlog.debug("Execution time : %.3f seconds" % (time.time() - START_TIME))
    simlog.debug("Simulation time : %.1f seconds" % (sim_loop.get_simulation_time()))
    simlog.debug("Amount of traveler generated : %d" % total_generated)
