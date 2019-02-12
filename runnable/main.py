#! /usr/bin/env python3
# coding: utf-8
import logging
import time

import simulator.sim_loop
from settings import network
from simulator.traveler_generator import total_generated

"""Fichier principal du projet """

"""Initialisation"""
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

START_TIME = time.time()

sim_loop = simulator.sim_loop.SimLoop()

network.load()

"""Start"""
if __name__ == "__main__":
    logging.debug("Simulation starts")
    print("lol")
    simulator.sim_loop.run_simulation(sim_loop=sim_loop)
    logging.debug("Execution time : %.3f seconds" % (time.time() - START_TIME))
    logging.debug("Simulation time : %.1f seconds" % (simulator.sim_loop.get_simulation_time()))
    logging.debug("Amount of traveler generated : %d" % total_generated)
