import time

from settings import network
from settings import simlog
from simulator import sim_loop

"""Fichier principal du projet -- absence d'interface graphique """

"""Initialisation"""
START_TIME = time.time()
network.load()

"""Start"""
if __name__ == "__main__":
    simlog.debug("Simulation starts")
    sim_loop.start_simulation()
    simlog.debug("Execution time : %.3f seconds" % (time.time() - START_TIME))
    simlog.debug("Simulation time : %.1f seconds" % (sim_loop.get_simulated_time()))
