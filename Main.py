#! /usr/bin/env python3
# coding: utf-8

#import Interface.<fichier> as Interf 
#import Model.<fichier> as Model
#import Simulator.<fichier> as SimpyConf
import time
import simpy.rt
from Simulateur import Poisson

test_seconds_duration = 10

'''Il s'agit du fichier principal de notre projet qui lance les différentes parties et fait le lien entre elles'''
start_time = time.time()
poisson = Poisson.Poisson()
print(poisson.generate())


'''Load <...>'''
env = simpy.rt.RealtimeEnvironment(factor=0.1)
env.run(until=test_seconds_duration*10)



'''Building <...>'''
#<...>
print("Execution time : " + time.strftime("%M:%S", time.localtime(time.time() - start_time)))

'''Establish <...>'''

