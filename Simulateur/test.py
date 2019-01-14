import time
import simpy.rt

start = time.time()
env = simpy.rt.RealtimeEnvironment(factor=0.1)

env.run(until=20)
