#! /usr/bin/env python3
# coding: utf-8
import logging
import sys
import time

import simpy

from settings import config
from settings import network
from simulator import sim_loop
from simulator import traveler_generator

"""Fichier principal du projet """

"""Initialisation"""
path_to_add_array = sys.path[0].split("/")
del path_to_add_array[len(path_to_add_array) - 1]
sys.path.append("/".join(path_to_add_array))
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
network.load()

SIM_DURATION = int(config.sim['duration'])
SIM_TICK = float(config.sim['tick'])
START_TIME = time.time()
sim_environment = None

real_time_boolean = config.sim['real_time']
if real_time_boolean in ['false', 'False']:
    sim_environment = simpy.Environment()
else:
    sim_environment = simpy.rt.RealtimeEnvironment(factor=SIM_TICK)

simpy.rt.RealtimeEnvironment(factor=SIM_TICK)

sim_loop = sim_loop.SimLoop(env=sim_environment, sim_tick=SIM_TICK)

"""Start"""
if __name__ == "__main__":
    sim_environment.process(sim_loop.loop())
    logging.debug("Simulation starts")
    sim_environment.run(until=SIM_DURATION)
    logging.debug("Execution time : %.3f seconds" % (time.time() - START_TIME))
    logging.debug("Total generated : %d" % traveler_generator.total_generated)
