#! /usr/bin/env python3
# coding: utf-8
import logging
import time
import os
import simpy.rt

from settings import config
from simulator import converter
from simulator import sim_loop
from settings import load_network

"""Initialisation"""
CONFIG_PATH = 'resources/config.ini'
config.load(CONFIG_PATH)
converter.load()

SIM_DURATION = int(config.sim['duration'])
SIM_TICK = float(config.sim['tick'])
START_TIME = time.time()
simpy_environment = simpy.rt.RealtimeEnvironment(factor=SIM_TICK)
sim_loop = sim_loop.SimLoop(env=simpy_environment, sim_tick=SIM_TICK)

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

"""Start"""
if __name__ == "__main__":
    simpy_environment.process(sim_loop.loop())
    print("Simulation starts")
    simpy_environment.run(until=SIM_DURATION)
    print("Execution time : ", round(time.time() - START_TIME, 3), "seconds")

""""Load of network"""
load_network.load(str(config.model['network_file']))
