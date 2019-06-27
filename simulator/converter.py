import random
from math import floor

import scipy.stats

from model import station
from settings import config
from settings import simlog
from simulator import sim_loop

_city_percent = None
_activity_and_residential_percent = None
_activity_and_residential_fluctuation = None
_ascent_descent_duration = None
_morning_peak_hour = None
_evening_peak_hour = None


def init_converter():
    global _city_percent
    global _activity_and_residential_percent
    global _activity_and_residential_fluctuation
    global _ascent_descent_duration
    global _morning_peak_hour
    global _evening_peak_hour
    _city_percent = int(config.prob['city_percent'])
    _activity_and_residential_percent = int(config.prob['activity_and_residential_percent'])
    _activity_and_residential_fluctuation = int(config.prob['activity_and_residential_fluctuation'])
    _ascent_descent_duration = int(config.traveler['ascent_descent_duration'])
    _morning_peak_hour = int(config.traveler['morning_peak_hour'])
    _evening_peak_hour = int(config.traveler['evening_peak_hour'])

    if _activity_and_residential_fluctuation < 0 \
            or _activity_and_residential_fluctuation >= _activity_and_residential_percent:
        _activity_and_residential_fluctuation = floor(_activity_and_residential_percent / 2)


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


def station_probability(station_type, second, is_arrival=True):
    """
    This function gives you the probability to lead a traveler to a station_type
    at a certain time in second. You can choose if the station is a departure or
    destination station.
    :param station_type: The type of station you want to find its probability
    :param second: The time in second
    :param is_arrival: If the station is a departure or destination station
    :return: The probability to lead a traveler to the chosen station_type at the given time
    """
    global _city_percent
    global _activity_and_residential_percent
    global _activity_and_residential_fluctuation
    global _ascent_descent_duration
    global _morning_peak_hour
    global _evening_peak_hour

    if None in (_city_percent, _activity_and_residential_percent, _activity_and_residential_fluctuation):
        simlog.error("Converter hasn't been loaded")
        return 0

    second = second % 86400
    mph = _morning_peak_hour
    eph = _evening_peak_hour
    gaussian_factor = 250 * (_activity_and_residential_fluctuation / 100)
    result = 0
    if station_type == station.Type.CITY:
        result = _city_percent
    if station_type == station.Type.ACTIVITY:
        if is_arrival:
            if second < 43200:
                result = _activity_and_residential_percent + gaussian_factor * scipy.stats.norm.pdf(
                    seconds_to_decimal_hour(second), mph, 1)
            else:
                result = _activity_and_residential_percent - gaussian_factor * scipy.stats.norm.pdf(
                    seconds_to_decimal_hour(second), eph, 1)
        else:
            if second < 43200:
                result = _activity_and_residential_percent - gaussian_factor * scipy.stats.norm.pdf(
                    seconds_to_decimal_hour(second), mph, 1)
            else:
                result = _activity_and_residential_percent + gaussian_factor * scipy.stats.norm.pdf(
                    seconds_to_decimal_hour(second), eph, 1)
    if station_type == station.Type.RESIDENTIAL:
        if is_arrival:
            if second < 43200:
                result = _activity_and_residential_percent - gaussian_factor * scipy.stats.norm.pdf(
                    seconds_to_decimal_hour(second), mph, 1)
            else:
                result = _activity_and_residential_percent + gaussian_factor * scipy.stats.norm.pdf(
                    seconds_to_decimal_hour(second), eph, 1)
        else:
            if second < 43200:
                result = _activity_and_residential_percent + gaussian_factor * scipy.stats.norm.pdf(
                    seconds_to_decimal_hour(second), mph, 1)
            else:
                result = _activity_and_residential_percent - gaussian_factor * scipy.stats.norm.pdf(
                    seconds_to_decimal_hour(second), eph, 1)
    return round(result / 100, 2)


def random_ascent_descent_duration():
    """
    :return: A value between [|time-2, time+2|]. time is the defined duration (in the config file)
    for ascent and descent events.
    """
    global _ascent_descent_duration
    random_seconds = random.randrange(_ascent_descent_duration - 2, _ascent_descent_duration + 2, 1)
    return random_seconds * sim_loop.get_tick_per_second()


def serialize_clock():
    return {
        'jsonType': 'time',
        'day': now_to_day(),
        'time': seconds_to_string(now_to_seconds()),
        'speed': sim_speed_to_string(),
        'accelerateJerky': (0, 1)[sim_loop.get_visualized_tick_duration() == 0],
        'decelerateJerky': (0, 1)[sim_loop.get_initial_sim_tick() * 4 <= sim_loop.get_sim_tick()]
    }
