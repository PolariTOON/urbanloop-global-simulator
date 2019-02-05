import logging
from enum import Enum

import simpy

from qt.main_window import window
from model import capsule
from model import station
from settings import config
from simulator.ascent_generator import AscentGenerator
from simulator.traveler_generator import TravelerGenerator


class SimState(Enum):
    RUNNING = 0
    PAUSED = 1
    KILLED = 2


_env = None
_current_tick = 0
_sim_state = None
_sim_tick = 0.05
_start_hour = None
_sim_tick_variation = list()
_loop_process = None
_endless_quit_event = None


class SimLoop:
    def __init__(self):
        global _env
        global _sim_state
        global _sim_tick
        global _start_hour
        global _endless_quit_event
        _sim_tick = float(config.sim['tick'])
        _load_env()
        _start_hour = int(config.sim['start_hour'])
        self.traveler_generator = TravelerGenerator()
        self.ascent_generator = AscentGenerator()
        self.tick_event = _env.event()
        self.is_endless = False
        _endless_quit_event = _env.event()

        if config.sim['endless'] in ['true', 'True']:
            self.is_endless = True

        if config.sim['auto_run'] in ['false', 'False']:
            _sim_state = SimState.PAUSED
        else:
            _sim_state = SimState.RUNNING

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
        global _current_tick
        while True:
            if _sim_state == SimState.RUNNING:
                _env.process(self.tick())
                _env.process(self.ascent_generator.generate())
                if is_frequency(1):
                    _env.process(self.traveler_generator.generate())
                # print(_current_tick)
                if window is not None:
                    window.refresh()
                yield _env.timeout(1)
            elif _sim_state == SimState.KILLED:
                yield _env.process(_env.exit())


def _process_loop(sim_loop):
    """
    This function processes the loop function of the sim_loop instance on the simulation environment _env
    :param sim_loop: The sim_loop instance
    """
    global _env
    global _loop_process

    _loop_process = _env.process(sim_loop.loop())


def _load_env():
    """
    Load the simulation environment with configuration
    """
    global _env
    real_time_boolean = config.sim['real_time']
    if real_time_boolean in ['false', 'False']:
        _env = simpy.Environment()
    else:
        _env = simpy.rt.RealtimeEnvironment(factor=_sim_tick)


def _change_sim_tick(value=_sim_tick):
    """
    Change the current sim_tick value
    /!\ This function is disabled in case of real time simulation
    :param value: The desired new sim_tick value
    """

    if type(_env) is simpy.rt.RealtimeEnvironment:
        logging.warning("You can't change the sim_tick in a real-time environment")
        return

    global _sim_tick
    global _sim_tick_variation

    last_current_tick_variation = 0
    if len(_sim_tick_variation) > 0:
        last_current_tick_variation = _sim_tick_variation[-1][0]

    _sim_tick_variation.append((_current_tick - last_current_tick_variation, _sim_tick))
    old_value = get_tick_per_second()
    _sim_tick = value

    logging.debug("Changing sim ticks per seconds from %f to %f" % (old_value, get_tick_per_second()))


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
    logging.debug("Changing SimState to %s" % sim_state.name)
    global _sim_state
    _sim_state = sim_state


def run_simulation(sim_loop=None):
    """
    Run the simulation with the loop_process
    """
    global _env

    if sim_loop is None:
        sim_loop = SimLoop()

    _process_loop(sim_loop)

    if sim_loop.is_endless:
        global _endless_quit_event
        _env.run(_endless_quit_event)
        return

    _env.run(until=int(config.sim['duration']))


def quit_endless_simulation():
    global _env
    global _endless_quit_event

    def _trigger():
        yield _endless_quit_event.succeed()

    _env.process(_trigger())


def pause_simulation():
    global _loop_process
    change_state(SimState.PAUSED)
    _loop_process.interrupt()


def stop_simulation():
    logging.debug("Stopping simulation")
    capsule.reset_simulation()
    station.reset_simulation()
    if window is not None:
        window.refresh()
    change_state(SimState.KILLED)


def reset_simulation():
    """
    Reset the current simulation at
    """
    global _current_tick
    global _sim_tick_variation
    global _loop_process
    logging.warning("Resetting the simulation")
    change_state(SimState.PAUSED)
    _loop_process.interrupt()
    capsule.reset_simulation()
    station.reset_simulation()
    _current_tick = 0
    _sim_tick_variation = list()
    change_state(SimState.RUNNING)
    run_simulation()


def accelerate_sim():
    """
    Multiply the current sim_tick by 2, so there are more ticks per simulated second
    """
    _change_sim_tick(value=(_sim_tick * 2))


def decelerate_sim():
    """
    Divide the current sim_tick by 2, so there are less ticks per simulated second
    """
    _change_sim_tick(value=(_sim_tick * 2))


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


def get_simulation_time():
    """
    :return: The total simulated time, in seconds
    """
    global _sim_tick_variation
    result = 0
    for ticks, a_sim_tick in _sim_tick_variation:
        result += ticks * a_sim_tick

    last_current_tick_variation = 0
    if len(_sim_tick_variation) > 0:
        last_current_tick_variation = _sim_tick_variation[-1][0]

    result += ((_current_tick - last_current_tick_variation) * _sim_tick)

    return result
