from enum import Enum

from settings import config
from simulator.ascent_generator import AscentGenerator
from simulator.traveler_generator import TravelerGenerator


class SimState(Enum):
    RUNNING = 0
    PAUSED = 1
    KILLED = 2


_env = None
_current_tick = 0
_sim_state = SimState.RUNNING
_sim_tick = 0.05
_start_hour = None


class SimLoop:
    def __init__(self, sim_env, sim_tick):
        global _env
        global _sim_state
        global _sim_tick
        global _start_hour
        _env = sim_env
        _sim_tick = sim_tick
        _start_hour = int(config.sim['start_hour'])
        self.traveler_generator = TravelerGenerator()
        self.ascent_generator = AscentGenerator()
        self.tick_event = _env.event()

        if config.sim['auto_run'] in ['false', 'False']:
            _sim_state = SimState.PAUSED

    def tick(self):
        """
        This function triggers the tick_event
        The tick_event update the current_tick.
        It should be used to frequency process
        """
        global _current_tick
        _current_tick += 1
        yield self.tick_event.succeed()
        self.tick_event = _env.event()

    def loop(self):
        """
        This function is the main process loop of the simulation.
        You can create several independents process while the
        SimState is RUNNING.
        """
        while True:
            if _sim_state == SimState.RUNNING:
                _env.process(self.tick())
                _env.process(self.ascent_generator.generate())
                if is_frequency(1):
                    _env.process(self.traveler_generator.generate())
                yield _env.timeout(1)
            elif _sim_state == SimState.KILLED:
                yield _env.process(_env.exit())


def is_frequency(seconds):
    """
    :param seconds: The desired frequency
    :return: Boolean, if the current_tick is in phase with the given frequency
    """
    return get_current_tick() % (seconds / _sim_tick) == 0


def change_state(sim_state=SimState.RUNNING):
    """
    :param sim_state: The desired simulation state
    """
    global _sim_state
    _sim_state = sim_state


def get_env():
    """
    :return: The simulation environment
    """
    return _env


def get_current_tick():
    """
    :return: The simulation current tick
    """
    return _current_tick


def get_state():
    """
    :return: The simulation state
    """
    return _sim_state


def get_sim_tick():
    """
    :return: The simulation tick
    """
    return _sim_tick


def get_tick_per_second():
    """
    :return: The simulation ticks per second
    """
    return 1 / _sim_tick


def get_start_hour():
    """
    :return: The simulation start hour
    """
    return _start_hour
