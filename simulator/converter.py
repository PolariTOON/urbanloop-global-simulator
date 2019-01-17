import logging
import scipy.stats

from model.station import Type
from settings import config


# TODO thibault specification


neutral_percent = int(config.model['neutral_percent'])
city_percent = int(config.model['city_percent'])
activity_and_residential_percent = int(config.model['activity_and_residential_percent'])
activity_and_residential_fluctuation = int(config.model['activity_and_residential_fluctuation'])
morning_peak_hour = int(config.model['morning_peak_hour'])
evening_peak_hour = int(config.model['evening_peak_hour'])

if activity_and_residential_fluctuation < 0 or activity_and_residential_fluctuation >= activity_and_residential_percent:
    activity_and_residential_fluctuation = round(activity_and_residential_percent / 2)


def seconds_to_string(seconds):
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return '%02d:%02d:%02d' % (hours, minutes, secs)


def seconds_to_decimal_hour(seconds):
    return round(seconds / 3600, 2)


def now_to_seconds(env, sim_tick, start_hour=0):
    return env.now * sim_tick + start_hour * 3600


def now_to_floor_hour(now_in_seconds):
    return round((now_in_seconds % 86400) / 3600)


# noinspection PyTypeChecker
def station_probability(station_type, second, is_arrival=True):
    if neutral_percent is None or city_percent is None or activity_and_residential_percent is None or activity_and_residential_fluctuation is None:
        logging.error("Converter hasn't been loaded")
        return 0

    second = second % 86400
    mph = morning_peak_hour
    eph = evening_peak_hour
    gaussian_factor = 250 * (activity_and_residential_fluctuation / 100)
    result = 0
    if station_type == Type.NEUTRAL:
        result = neutral_percent
    if station_type == Type.CITY:
        result = city_percent
    if station_type == Type.ACTIVITY:
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
    if station_type == Type.RESIDENTIAL:
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
