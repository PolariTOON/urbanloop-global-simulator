import time
from enum import Enum

import simpy

from model import capsule as model_capsule
from model import station
from model import loop as model_loop
from settings import config
from settings import simlog
from simulator import ascent_generator
from simulator import traveler_generator
#TODO fixer from stats import stats_record


class SimState(Enum):
    RUNNING = 0
    PAUSED = 1
    KILLED = 2


_env = None
_current_tick = 0
_sim_state = None
_sim_tick = 0.05
_visualized_tick_duration = 0.05
_start_hour = None
_sim_tick_variations = list()
_endless_quit_event = None
recorder = None


class SimLoop:
    def __init__(self, is_visualized=False):
        global _env
        global _sim_state
        global _sim_tick
        global _visualized_tick_duration
        global _start_hour
        global _endless_quit_event
        global recorder
        _sim_tick = float(config.sim['tick'])
        _visualized_tick_duration = _sim_tick
        _start_hour = int(config.sim['start_hour'])
        _sim_state = SimState.RUNNING
        self.is_real_time = False
        self.is_endless = False
        self.is_visualized = is_visualized
#TODO fixer <<<<<<< HEAD
        # recorder = stats_record.StatsRecorder(0)

#TODO fixer=======
        self.traveler_generator = traveler_generator.TravelerGenerator()
        self.ascent_generator = ascent_generator.AscentGenerator()
#TODO fixer >>>>>>> 282cf5a368e4a13a6846f9868957342a6ee3af1a

        if config.sim['real_time'] in ['true', 'True']:
            self.is_real_time = True
        if config.sim['endless'] in ['true', 'True']:
            self.is_endless = True

        _load_env(self.is_real_time)
        self.tick_event = _env.event()
        _endless_quit_event = _env.event()
        _env.process(self.loop())  # Register the loop process in the simulation environment

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
        global recorder
        tick_start_time = 0
        while True:
            if is_running():
                loop_sleep_boolean = self.is_visualized and not self.is_real_time and _visualized_tick_duration != 0
                if loop_sleep_boolean:
                    tick_start_time = time.perf_counter()
                
                if _modulo_on_seconds(30): # stats
                    # loops
                    loops = []
                    capsules = {}
                    for loop_name in model_loop.all_loops:
                        loops.append(model_loop.get_by_name(loop_name))
                        capsules[loop_name] = 0
                    for capsule in model_capsule._capsules:
                        capsules[capsule.loop.name] += 1
                    #TODO fixer for loop in loops:
                        #TODO fixerrecorder.add_capsule_average_loop(capsules[loop.name], loop)

                _env.process(self.tick())
                _env.process(self.ascent_generator.generate())
                if _modulo_on_seconds(1):
                    _env.process(self.traveler_generator.generate())
                if not _current_tick == 0 and _modulo_on_seconds(120):
                    station.fill_and_full_stations()

                yield _env.timeout(1)

                if loop_sleep_boolean:
                    sleep_time = _visualized_tick_duration - (time.perf_counter() - tick_start_time)
                    time.sleep(max(0.0, sleep_time))
            elif is_killed():
                reset_simulation_parameters()
                if self.is_endless:
                    _quit_endless_simulation()
                else:
                    yield _env.process(_env.exit())
                return


def _load_env(is_real_time=False):
    """
    Load the simulation environment with configuration, real_time or not
    """
    global _env
    if is_real_time:
        _env = simpy.rt.RealtimeEnvironment(factor=_sim_tick)
    else:
        _env = simpy.Environment()


def _change_sim_tick(value=_sim_tick):
    """
    Change the current sim_tick value. Bigger is the sim_tick value,
    more jerky the simulation will be. Use this to speed up (really)
    the simulation. This function adds in the variations list, the tuple :
    (start_tick, tick_duration, sim_tick) in _sim_tick_variations
    /!\ This function is disabled in case of real time simulation
    :param value: The desired new sim_tick value
    """
    if type(_env) is simpy.rt.RealtimeEnvironment:
        simlog.warn("You can't change the sim_tick in a real-time environment")
        return

    if value <= 0:
        simlog.warn("The sim_tick needs to be greater than zero")
        return

    global _sim_tick
    global _sim_tick_variations

    if _sim_tick_variations:
        # Not empty case
        start_tick = _sim_tick_variations[-1][0] + _sim_tick_variations[-1][1]
        tick_duration = _current_tick - start_tick
        _sim_tick_variations.append((start_tick, tick_duration, _sim_tick))
    else:
        # Empty case
        _sim_tick_variations.append((0, _current_tick, _sim_tick))

    _sim_tick = value
    simlog.warn("Changing _sim_tick. One tick equals now %f seconds" % _sim_tick)


def _modulo_on_seconds(seconds):
    """
    This function will return True every simulated seconds. Seconds must be
    greater or equal to 1.
    :param seconds: The desired modulo
    :return: Boolean, if the current_tick is in phase with the given frequency
    """
    if (seconds / _sim_tick) < 1 or seconds < 1:
        return True
    return get_current_tick() % (seconds / _sim_tick) == 0


def accelerate_simulation():
    global _sim_tick
    global _visualized_tick_duration

    initial_sim_tick = get_initial_sim_tick()

    if _visualized_tick_duration > 0:
        _visualized_tick_duration /= 2
        if _visualized_tick_duration < initial_sim_tick * pow(2, -7):
            _visualized_tick_duration = 0
        return

    if _sim_tick < initial_sim_tick * pow(2, 8):
        _change_sim_tick(_sim_tick * 2)


def decelerate_simulation():
    global _sim_tick
    global _visualized_tick_duration

    initial_sim_tick = get_initial_sim_tick()

    if _sim_tick > initial_sim_tick:
        _change_sim_tick(_sim_tick / 2)
        return

    if _visualized_tick_duration < initial_sim_tick:
        _visualized_tick_duration *= 2
        if _visualized_tick_duration == 0:
            _visualized_tick_duration = initial_sim_tick * pow(2, -7)


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
    #TODO fixerglobal recorder
    #TODO fixer recorder.stop_listen(get_simulated_time())

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
    #TODO fixer global recorder
    #TODO fixer recorder.stop_listen()

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
    global _env, _current_tick, _sim_state, _sim_tick, _visualized_tick_duration
    global _start_hour, _sim_tick_variations, _endless_quit_event

    if _sim_state != SimState.KILLED:
        return

    simlog.warn("Resetting the simulation parameters")
    model_capsule.reset_simulation()
    station.reset_simulation()
    _current_tick = 0
    _sim_tick = 0.05
    _visualized_tick_duration = 0.05
    _start_hour = None
    _sim_tick_variations = list()


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


def is_killed():
    """
    :return: True if the simulation is currently paused
    """
    return _sim_state == SimState.KILLED


def get_sim_tick():
    """
    :return: The simulation tick
    """
    return _sim_tick


def get_initial_sim_tick():
    """
    :return: The _sim_tick value at the start of simulation
    """
    if _sim_tick_variations:
        return _sim_tick_variations[0][2]
    return _sim_tick


def get_visualized_tick_duration():
    """
    :return: The visualized tick duration
    """
    return _visualized_tick_duration


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


def get_simulated_time(tick=None):
    """
    :return: The total simulated time, in seconds. This function takes
    into account the sim_tick variation.
    """
    global _sim_tick_variations

    if tick is None or tick > get_current_tick():
        tick = get_current_tick()

    if not _sim_tick_variations:
        # Empty case
        return tick * _sim_tick

    result = 0
    for start_tick, tick_duration, sim_tick in _sim_tick_variations:
        if tick <= start_tick + tick_duration:
            return result + (tick - start_tick) * sim_tick
        result += tick_duration * sim_tick

    last_end_tick = _sim_tick_variations[-1][0] + _sim_tick_variations[-1][1]
    result += (tick - last_end_tick) * _sim_tick

    return result
