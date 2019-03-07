import time
from enum import Enum

import simpy

from model import capsule
from model import station
from runnable import web_app
from settings import config
from settings import simlog
from simulator import ascent_generator
from simulator import traveler_generator


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
_endless_quit_event = None


class SimLoop:
    def __init__(self, is_visualized=False):
        global _env
        global _sim_state
        global _sim_tick
        global _start_hour
        global _endless_quit_event
        _sim_tick = float(config.sim['tick'])
        _load_env()
        _start_hour = int(config.sim['start_hour'])
        _sim_state = SimState.RUNNING
        self.traveler_generator = traveler_generator.TravelerGenerator()
        self.ascent_generator = ascent_generator.AscentGenerator()
        self.tick_event = _env.event()
        self.is_endless = False
        self.is_visualized = is_visualized

        if config.sim['endless'] in ['true', 'True']:
            self.is_endless = True
            _endless_quit_event = _env.event()

        # Register the loop process in the simulation environment
        _env.process(self.loop())

    def tick(self):
        """
        This function triggers the tick_event
        The tick_event updateData the current_tick.
        It should be used to frequency process
        """
        global _current_tick
        _current_tick += 1
        yield self.tick_event.succeed()
        self.tick_event = _env.event()

    def loop(self):
        """
        This function is the main process station of the simulation.
        You can create several independents process while the
        SimState is RUNNING.
        """
        global _current_tick
        start = time.time()
        while True:
            if _sim_state == SimState.RUNNING:
                _env.process(self.tick())
                _env.process(self.ascent_generator.generate())
                if modulo_on_seconds(1):
                    _env.process(self.traveler_generator.generate())

                if not _current_tick == 0 and modulo_on_seconds(120):
                    station.fill_and_full_stations()

                if self.is_visualized:
                    time.sleep(0.0)

                yield _env.timeout(1)
            elif _sim_state == SimState.KILLED:
                reset_simulation_parameters()
                if self.is_endless:
                    _quit_endless_simulation()
                else:
                    yield _env.process(_env.exit())
                return


def _load_env():
    """
    Load the simulation environment with configuration, real_time or not
    """
    global _env
    real_time_boolean = config.sim['real_time']
    if real_time_boolean in ['false', 'False']:
        _env = simpy.Environment()
    else:
        _env = simpy.rt.RealtimeEnvironment(factor=_sim_tick)


def _change_sim_tick(value=_sim_tick):
    """
    Change the current sim_tick value. Bigger is the sim_tick value,
    more jerky the simulation will be. Use this to speed up (really)
    the simulation.
    /!\ This function is disabled in case of real time simulation
    :param value: The desired new sim_tick value
    """
    if type(_env) is simpy.rt.RealtimeEnvironment:
        simlog.warn("You can't change the sim_tick in a real-time environment")
        return

    global _sim_tick
    global _sim_tick_variation

    last_current_tick_variation = 0
    if len(_sim_tick_variation) > 0:
        last_current_tick_variation = _sim_tick_variation[-1][0]

    _sim_tick_variation.append((_current_tick - last_current_tick_variation, _sim_tick))
    old_value = get_tick_per_second()
    _sim_tick = value

    simlog.debug("Changing sim ticks per seconds from %f to %f" % (old_value, get_tick_per_second()))


def modulo_on_seconds(seconds):
    """
    This function will return True every simulated seconds.
    :param seconds: The desired modulo
    :return: Boolean, if the current_tick is in phase with the given frequency
    """
    if seconds / _sim_tick < 1:
        return True
    return get_current_tick() % (seconds / _sim_tick) == 0


def change_state(sim_state=SimState.RUNNING):
    """
    :param sim_state: The desired simulation state
    """
    simlog.debug("Changing SimState to %s" % sim_state.name)
    global _sim_state
    _sim_state = sim_state


def start_simulation(is_visualized=False):
    """
    Start the simulation for the first time. Use run_simulation_after_pause()
    to re-run the simulation after a PAUSED state.
    :param is_visualized: Set to True if the web_app.py is launched
    """
    global _env
    sim_loop = SimLoop(is_visualized=is_visualized)

    if sim_loop.is_endless:
        _env.run(_endless_quit_event)
        return
    _env.run(until=int(config.sim['duration']))


def run_simulation_after_pause():
    """
    Re-run the simulation after a PAUSED state.
    """
    simlog.warn("Simulation re-RUNNING")
    change_state(SimState.RUNNING)


def _quit_endless_simulation():
    """
    Stop an endless simulation by triggering the _endless_quit_event.
    This function should only be used in SimLoop.loop(), and asserts
    that the simulation is endless
    """
    global _env

    def _trigger():
        yield _endless_quit_event.succeed()

    _env.process(_trigger())


def stop_simulation():
    """
    Stop the simulation definitely. After call this method, The SimLoop.loop()
    function will manage the case endless or not, and reset all simulation parameters
    """
    simlog.warn("Simulation KILLED")
    change_state(SimState.KILLED)


def pause_simulation():
    """
    Pause the simulation. Call run_simulation_after_pause to restart the simulation
    """
    simlog.warn("Simulation PAUSED")
    change_state(SimState.PAUSED)


def reset_simulation_parameters():
    """
    Reset the current simulation parameters. The SimState needs to be KILLED
    """
    global _current_tick, _sim_state, _sim_tick_variation

    if _sim_state != SimState.KILLED:
        return

    simlog.warn("Resetting the simulation parameters")
    capsule.reset_simulation()
    station.reset_simulation()
    _current_tick = 0
    _sim_tick_variation = list()


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


def is_running():
    """
    :return: True if the simulation is currently started
    """
    return _sim_state == SimState.RUNNING


def is_paused():
    """
    :return: True if the simulation is currently paused
    """
    return _sim_state == SimState.PAUSED


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


def get_current_day():
    global _start_hour
    if _start_hour is None:
        # This case means that the simulation hasn't been started yet.
        return 0
    return 1 + int((_start_hour * 3600 + get_simulation_time()) / 86400)


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
