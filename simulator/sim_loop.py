from enum import Enum

import simpy
import time
from model import capsule
from model import sim_record
from model import station
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
_sim_state = SimState.RUNNING
_sim_tick = 0.05
_start_hour = None
_sim_tick_variation = list()
_loop_process = None
_endless_quit_event = None


class SimLoop:
    def __init__(self, is_recorded=False):
        global _env
        global _sim_state
        global _sim_tick
        global _start_hour
        global _endless_quit_event
        _sim_tick = float(config.sim['tick'])
        _load_env()
        _start_hour = int(config.sim['start_hour'])
        self.traveler_generator = traveler_generator.TravelerGenerator()
        self.ascent_generator = ascent_generator.AscentGenerator()
        self.tick_event = _env.event()
        self.is_endless = False
        self.is_recorded = is_recorded

        if config.sim['endless'] in ['true', 'True']:
            self.is_endless = True
            _endless_quit_event = _env.event()

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
        while True:
            if _sim_state == SimState.RUNNING:
                start = time.time()
                _env.process(self.tick())
                _env.process(self.ascent_generator.generate())
                if is_frequency(1):
                    _env.process(self.traveler_generator.generate())

                if not _current_tick == 0 and is_frequency(120):
                    station.fill_and_full_stations()

                if self.is_recorded:
                    sim_record.put_record()

                yield _env.timeout(1)
            elif _sim_state == SimState.KILLED:
                yield _env.process(_env.exit())


def _process_loop(sim_loop):
    """
    This function processes the station function of the sim_loop instance on the simulation environment _env
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
    simlog.debug("Changing SimState to %s" % sim_state.name)
    global _sim_state
    _sim_state = sim_state


def run_simulation(sim_loop=None, is_recorded=False):
    """
    Run the simulation with the loop_process
    """
    global _env

    if sim_loop is None:
        sim_loop = SimLoop(is_recorded=is_recorded)

    _process_loop(sim_loop)

    if sim_loop.is_endless:
        _env.run(_endless_quit_event)
        return

    _env.run(until=int(config.sim['duration']))


def quit_endless_simulation():
    """
    Stop an endless simulation by triggering the _endless_quit_event
    """
    global _env

    def _trigger():
        yield _endless_quit_event.succeed()

    _env.process(_trigger())


def pause_simulation():
    """
    Pause the simulation. Call run_simulation to restart the simulation
    """
    global _loop_process
    change_state(SimState.PAUSED)


def stop_simulation():
    """
    Stop the simulation definitely. All objects or stations are reset
    """
    simlog.debug("Stopping simulation")
    change_state(SimState.KILLED)
    capsule.reset_simulation()
    station.reset_simulation()
    sim_record.records.empty()
    if _endless_quit_event is not None:
        quit_endless_simulation()
        return


def reset_simulation():
    """
    Reset the current simulation at
    """
    global _current_tick
    global _sim_tick_variation
    global _loop_process
    simlog.warn("Resetting the simulation")
    change_state(SimState.PAUSED)
    _loop_process.interrupt()
    capsule.reset_simulation()
    station.reset_simulation()
    _current_tick = 0
    _sim_tick_variation = list()
    change_state(SimState.RUNNING)
    run_simulation()


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
