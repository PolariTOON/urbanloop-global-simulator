import time
import simpy.rt


def example(env):
    start = time.perf_counter()
    yield env.timeout(5000)
    end = time.perf_counter()
    print('Duration of one simulation time unit: %.2fs' % (end - start))



