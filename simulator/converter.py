import logging

import scipy.stats

from simulator import sim_loop  # import simulator.sim_loop as sim_loop
from model import station
from settings import config

neutral_percent = int(config.model['neutral_percent'])
city_percent = int(config.model['city_percent'])
activity_and_residential_percent = int(config.model['activity_and_residential_percent'])
activity_and_residential_fluctuation = int(config.model['activity_and_residential_fluctuation'])
morning_peak_hour = int(config.model['morning_peak_hour'])
evening_peak_hour = int(config.model['evening_peak_hour'])

if activity_and_residential_fluctuation < 0 or activity_and_residential_fluctuation >= activity_and_residential_percent:
    activity_and_residential_fluctuation = round(activity_and_residential_percent / 2)


def seconds_to_string(seconds):
    """
    This function transforms a second amount to a HH:MM:SS string format
    :param seconds: The amount of seconds you want to transform
    :return: The same amount in string with a HH:MM:SS format
    """
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return '%02d:%02d:%02d' % (hours, minutes, secs)


def seconds_to_decimal_hour(seconds):
    """
    This function transforms a second amount to a decimal hour
    For example 5400 seconds = 1,5 hour
    :param seconds: The amount of seconds you want to transform
    :return: The same amount in decimal hour
    """
    return round(seconds / 3600, 2)


def now_to_seconds():
    """
    :return: The current time in second
    """
    return sim_loop.get_env().now * sim_loop.get_sim_tick() + sim_loop.get_start_hour() * 3600


def seconds_to_floor_hour(seconds):
    """
    This function transforms an amount of seconds to the corresponding hour
    :param seconds: An amount of seconds
    :return: The corresponding hour
    """
    return round((seconds % 86400) / 3600)


# noinspection PyTypeChecker
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
    if neutral_percent is None or city_percent is None or activity_and_residential_percent is None or activity_and_residential_fluctuation is None:
        logging.error("Converter hasn't been loaded")
        return 0

    second = second % 86400
    mph = morning_peak_hour
    eph = evening_peak_hour
    gaussian_factor = 250 * (activity_and_residential_fluctuation / 100)
    result = 0
    if station_type == station.Type.NEUTRAL:
        result = neutral_percent
    if station_type == station.Type.CITY:
        result = city_percent
    if station_type == station.Type.ACTIVITY:
        if is_arrival:
            if second < 43200:
                result = activity_and_residential_percent + gaussian_factor * scipy.stats.norm.pdf(
                    seconds_to_decimal_hour(second), mph, 1)
            else:
                result = activity_and_residential_percent - gaussian_factor * scipy.stats.norm.pdf(
                    seconds_to_decimal_hour(second), eph, 1)
        else:
            if second < 43200:
                result = activity_and_residential_percent - gaussian_factor * scipy.stats.norm.pdf(
                    seconds_to_decimal_hour(second), mph, 1)
            else:
                result = activity_and_residential_percent + gaussian_factor * scipy.stats.norm.pdf(
                    seconds_to_decimal_hour(second), eph, 1)
    if station_type == station.Type.RESIDENTIAL:
        if is_arrival:
            if second < 43200:
                result = activity_and_residential_percent - gaussian_factor * scipy.stats.norm.pdf(
                    seconds_to_decimal_hour(second), mph, 1)
            else:
                result = activity_and_residential_percent + gaussian_factor * scipy.stats.norm.pdf(
                    seconds_to_decimal_hour(second), eph, 1)
        else:
            if second < 43200:
                result = activity_and_residential_percent + gaussian_factor * scipy.stats.norm.pdf(
                    seconds_to_decimal_hour(second), mph, 1)
            else:
                result = activity_and_residential_percent - gaussian_factor * scipy.stats.norm.pdf(
                    seconds_to_decimal_hour(second), eph, 1)
    return round(result / 100, 2)
