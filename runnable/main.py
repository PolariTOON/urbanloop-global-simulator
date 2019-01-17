#! /usr/bin/env python3
# coding: utf-8
import sys
path_to_add_array = sys.path[0].split("/")
del path_to_add_array[len(path_to_add_array)-1]
sys.path.append("/".join(path_to_add_array))

import logging
import time

import simpy

from settings import config
from settings import network
from simulator import sim_loop

"""Initialisation"""
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
network.load()

SIM_DURATION = int(config.sim['duration'])
SIM_TICK = float(config.sim['tick'])
START_TIME = time.time()
sim_environment = simpy.rt.RealtimeEnvironment(factor=SIM_TICK)

sim_loop = sim_loop.SimLoop(env=sim_environment, sim_tick=SIM_TICK)

"""Start"""
if __name__ == "__main__":
    sim_environment.process(sim_loop.loop())
    logging.debug("Simulation starts")
    sim_environment.run(until=SIM_DURATION)
    logging.debug("Execution time : %.3f seconds" % (time.time() - START_TIME))
