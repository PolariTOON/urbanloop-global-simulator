import logging
from enum import Enum

from settings import config
from simulator.ascent_generator import ClimbGenerator
from simulator.traveler_generator import TravelerGenerator


class SimState(Enum):
    RUNNING = 0
    SLEEP = 1
    KILLED = 2


class SimLoop:
    def __init__(self, env, sim_tick):
        self.env = env
        self.sim_tick = sim_tick
        self.sim_state = SimState.RUNNING
        self.traveler_generator = TravelerGenerator(env=self.env)
        self.climb_generator = ClimbGenerator(env=self.env)
        self.start_hour = int(config.sim['start_hour'])
        self.tick_event = self.env.event()
        self.current_tick = 0
        self.event = self.env.event()

    def tick(self):
        """
        This function triggers the tick_event
        The tick_event update the current_tick.
        It should be used to frequency process
        """
        self.current_tick += 1
        yield self.tick_event.succeed()
        self.tick_event = self.env.event()

    def loop(self):
        """
        This function is the main process loop of the simulation.
        You can create several independents process while the
        SimState is RUNNING.
        """
        while True:
            if self.sim_state == SimState.RUNNING:
                self.env.process(self.tick())
                self.env.process(self.climb_generator.generate())
                if self.is_frequency(1):
                    self.env.process(self.traveler_generator.generate(start_hour=self.start_hour))
                yield self.env.timeout(1)
            elif self.sim_state == SimState.SLEEP:
                logging.warning("SLEEP State")
            elif self.sim_state == SimState.KILLED:
                logging.warning("KILLED State")
                yield self.env.process(self.env.exit())

    def is_frequency(self, seconds):
        """
        :param seconds: The desired frequency
        :return: Boolean, if the current_tick is in phase with the given frequency
        """
        return self.current_tick % (1 / self.sim_tick) == 0

    def exit(self):
        self.sim_state = SimState.KILLED
