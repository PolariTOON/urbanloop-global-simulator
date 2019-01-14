#! /usr/bin/env python3
# coding: utf-8

import simpy.rt
import time
from Simulator import FlowGenerator

"""Initialisation"""
SIM_DURATION = 60
SIM_TICK = 0.05
START_TIME = time.time()
simpy_environment = simpy.rt.RealtimeEnvironment(factor=SIM_TICK)
flow_generator = FlowGenerator.FlowGenerator(simpy_environment)


"""Start"""
if __name__ == "__main__":
    simpy_environment.process(flow_generator.generate_traveler(env=simpy_environment, sim_tick=SIM_TICK))
    simpy_environment.run(until=SIM_DURATION)
    print("Execution time : ", round(time.time() - START_TIME, 3), "seconds")

