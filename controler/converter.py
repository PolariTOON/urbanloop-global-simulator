"""
Cette classe contient des fonctions utilitaires sur le temps de la simulation
"""

import random
from math import floor

from simulator import sim_loop


class Converter:
    # TODO : les arguments proviennent de config
    def __init__(self, city_percent=None, activity_and_residential_percent=None,
                 activity_and_residential_fluctuation=None, ascent_descent_duration=None, morning_peak_hour=None,
                 evening_peak_hour=None):
        self.city_percent = city_percent
        self.activity_and_residential_percent = activity_and_residential_percent
        self.activity_and_residential_fluctuation = activity_and_residential_fluctuation
        self.ascent_descent_duration = ascent_descent_duration
        self.morning_peak_hour = morning_peak_hour
        self.evening_peak_hour = evening_peak_hour

        if self.activity_and_residential_fluctuation < 0 or self.activity_and_residential_fluctuation >= self.activity_and_residential_percent:
            self.activity_and_residential_fluctuation = floor(self.activity_and_residential_percent / 2)

    def random_ascent_descent_duration(self):
        """
        :return: A value between [|time-2, time+2|]. time is the defined duration (in the config file)
        for ascent and descent events.
        """
        random_seconds = random.randrange(self.ascent_descent_duration - 2, self.ascent_descent_duration + 2, 1)
        return random_seconds * sim_loop.get_tick_per_second()


def sim_speed_to_string():
    """
    :return: This function can only be used in visualized mode.
    """
    sim_tick = sim_loop.get_sim_tick()
    view_tick = sim_loop.get_visualized_tick_duration()
    initial_tick = sim_loop.get_initial_sim_tick()
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


def now_to_day():
    """
    :return: The current day. This function takes into account the
    sim_tick variations.
    """
    # Start at Day 1
    start_hour = sim_loop.get_start_hour()
    if start_hour is None:
        # This case means that the simulation hasn't been started yet.
        return 1
    return 1 + int((start_hour * 3600 + sim_loop.get_simulated_time()) / 86400)


def now_to_seconds():
    """
    :return: The current time in second. This function takes into account the
    sim_tick variations.
    """
    if sim_loop.get_start_hour() is None:
        return -1
    return sim_loop.get_start_hour() * 3600 + sim_loop.get_simulated_time()


def seconds_to_floor_hour(seconds):
    """
    This function transforms an amount of seconds to the corresponding hour
    :param seconds: An amount of seconds
    :return: The corresponding hour
    """
    return floor((seconds % 86400) / 3600)


def serialize_clock():
    return {
        'jsonType': 'time',
        'day': now_to_day(),
        'time': seconds_to_string(now_to_seconds()),
        'speed': sim_speed_to_string(),
        'accelerateJerky': (0, 1)[sim_loop.get_visualized_tick_duration() == 0],
        'decelerateJerky': (0, 1)[sim_loop.get_initial_sim_tick() * 4 <= sim_loop.get_sim_tick()]
    }
