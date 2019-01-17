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
        self.traveler_generator = traveler_generator.TravelerGenerator(env)
        self.start_hour = int(config.sim['start_hour'])
        self.tick_event = self.env.event()
        self.current_tick = 0

    def tick(self):
        self.current_tick += 1
        yield self.tick_event.succeed()
        self.tick_event = self.env.event()

    def loop(self):
        while True:
            if self.sim_state == SimState.RUNNING:
                self.env.process(self.tick())

                if self.current_tick % (1 / self.sim_tick) == 0:
                    self.env.process(self.traveler_generator.generate_traveler(
                        env=self.env,
                        sim_tick=self.sim_tick,
                        start_hour=self.start_hour)
                    )
                yield self.env.timeout(1)
            elif self.sim_state == SimState.SLEEP:
                logging.warning("SLEEP State")
            elif self.sim_state == SimState.KILLED:
                logging.warning("KILLED State")
                yield self.env.process(self.env.exit())

    def exit(self):
        self.sim_state = SimState.KILLED
