#! /usr/bin/env python3
# coding: utf-8
import logging
import time

import simpy

from settings import config
from settings import network
from simulator import sim_loop
from simulator import traveler_generator

"""Fichier principal du projet """

"""Initialisation"""
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

SIM_DURATION = int(config.sim['duration'])
SIM_TICK = float(config.sim['tick'])
START_TIME = time.time()
sim_environment = None

real_time_boolean = config.sim['real_time']
if real_time_boolean in ['false', 'False']:
    sim_environment = simpy.Environment()
else:
    sim_environment = simpy.rt.RealtimeEnvironment(factor=SIM_TICK)

sim_loop = sim_loop.SimLoop(sim_env=sim_environment, sim_tick=SIM_TICK)
network.load()

"""Start"""
if __name__ == "__main__":
    sim_environment.process(sim_loop.loop())
    logging.debug("Simulation starts")
    sim_environment.run(until=SIM_DURATION)
    logging.debug("Execution time : %.3f seconds" % (time.time() - START_TIME))
    logging.debug("Simulation time : %.1f seconds" % (sim_environment.now * SIM_TICK))
    logging.debug("Amount of traveler generated : %d" % traveler_generator.total_generated)
