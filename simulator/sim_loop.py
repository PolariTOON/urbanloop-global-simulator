import logging
from enum import Enum

from settings import config
from simulator import traveler_generator


class SimState(Enum):
    RUNNING = 0
    SLEEP = 1
    KILLED = 2


class SimLoop:
    def __init__(self, env, sim_tick):
        self.env = env
        self.sim_tick = sim_tick
        self.sim_state = SimState.RUNNING
        self.flow_generator = traveler_generator.FlowGenerator(env)
        self.start_hour = int(config.sim['start_hour'])

    def test(self):
        print("test at %d" % self.env.now)
        if self.env.now > 30:
            self.sim_state = SimState.KILLED
        yield self.env.timeout(1)

    def loop(self):
        while True:
            if self.sim_state == SimState.RUNNING:
                yield self.env.process(self.test())
                yield self.env.process(self.flow_generator.generate_traveler(
                    env=self.env,
                    sim_tick=self.sim_tick,
                    start_hour=self.start_hour)
                )
            elif self.sim_state == SimState.SLEEP:
                logging.warning("SLEEP State")
            elif self.sim_state == SimState.KILLED:
                logging.warning("KILLED State")
                yield self.env.process(self.env.exit())
