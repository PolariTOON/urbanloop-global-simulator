#! /usr/bin/env python3
# coding: utf-8
import time

import simpy.rt

from simulator import sim_loop

"""Initialisation"""
SIM_DURATION = 60
SIM_TICK = 0.05
START_TIME = time.time()
simpy_environment = simpy.rt.RealtimeEnvironment(factor=SIM_TICK)
sim_loop = sim_loop.SimLoop(env=simpy_environment, sim_tick=SIM_TICK)

"""Start"""
if __name__ == "__main__":
    simpy_environment.process(sim_loop.loop())
    print("Simulation starts")
    simpy_environment.run(until=SIM_DURATION)
    print("Execution time : ", round(time.time() - START_TIME, 3), "seconds")
