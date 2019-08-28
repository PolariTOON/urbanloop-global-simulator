"""
Ce fichier contient des fonctions utilitaires sur le temps de la simulation
"""
from math import floor


def sim_speed_to_string(sim_tick, view_tick, initial_tick):
    """
    This function can only be used in visualized mode.
    :param initial_tick: The _sim_tick value at the start of simulation
    :param view_tick: The visualized tick duration
    :param sim_tick: the simulation's tick
    :return: Return the speed of the simulation from string format.
    """
    if sim_tick == view_tick:
        return "RealTime"
    if view_tick == 0:
        if sim_tick > initial_tick:
            return "Jerky Mode<br>1 tick = %.2f seconds" % sim_tick
        else:
            return "Simulator speed"
    return "Speed x%d" % (initial_tick / view_tick)


def seconds_to_string(seconds):
    """
    This function transforms a second amount to a HH:MM:SS string format
    :param seconds: The amount of seconds you want to transform
    :return: The same amount in string with a HH:MM:SS format
    """
    if seconds < 0:
        return '--'

    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    hours %= 24
    return '%02d:%02d:%02d' % (hours, minutes, secs)


def seconds_to_decimal_hour(seconds):
    """
    This function transforms a second amount to a decimal hour
    For example 5400 seconds = 1,5 hour
    :param seconds: The amount of seconds you want to transform
    :return: The same amount in decimal hour
    """
    return round(seconds / 3600, 2)


def now_to_day(start_hour, simulated_time):
    """
    :param simulated_time: Total simulated time in seconds.
    :param start_hour: The simulation's start hour.
    :return: The current day. This function takes into account the sim_tick variations.
    """
    # Start at Day 1
    if start_hour is None:
        # This case means that the simulation hasn't been started yet.
        return 1
    return 1 + int((start_hour * 3600 + simulated_time) / 86400)


def now_to_seconds(start_hour, simulated_time):
    """
    :param simulated_time: Total simulated time in seconds.
    :param start_hour: The simulation's start hour.
    :return: The current time in second. This function takes into account the sim_tick variations.
    """
    if start_hour is None:
        return -1
    return start_hour * 3600 + simulated_time


def seconds_to_floor_hour(seconds):
    """
    This function transforms an amount of seconds to the corresponding hour
    :param seconds: An amount of seconds
    :return: The corresponding hour
    """
    return floor((seconds % 86400) / 3600)


def serialize_clock(view_tick, initial_tick, sim_tick, start_hour, simulated_time):
    """
    :param simulated_time: Total simulated time in seconds.
    :param start_hour: The simulation's start hour.
    :param view_tick: The visualized tick duration
    :param initial_tick: The _sim_tick value at the start of simulation
    :param sim_tick: The simulation's tick
    :return: A JSON array with the information about time of the simulation.
    """
    return {
        'jsonType': 'time',
        'day': now_to_day(start_hour, simulated_time),
        'time': seconds_to_string(now_to_seconds(start_hour, simulated_time)),
        'speed': sim_speed_to_string(sim_tick, view_tick, initial_tick),
        'accelerateJerky': (0, 1)[view_tick == 0],
        'decelerateJerky': (0, 1)[initial_tick * 4 <= sim_tick]
    }
