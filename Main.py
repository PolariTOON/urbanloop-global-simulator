#! /usr/bin/env python3
# coding: utf-8

#import Interface.<fichier> as Interf 
#import Model.<fichier> as Model
#import Simulator.<fichier> as SimpyConf
import time
import simpy.rt

test_seconds_duration = 10

'''Il s'agit du fichier principal de notre projet qui lance les différentes parties et fait le lien entre elles'''
t0=time.time()

'''Load <...>'''
env = simpy.rt.RealtimeEnvironment(factor=0.1)
env.run(until=test_seconds_duration*10)

'''Building <...>'''
#<...>
print("Execution time : " + time.strftime("%M:%S", time.localtime(time.time() - t0)))

'''Establish <...>'''

