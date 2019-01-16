import logging

import scipy.stats

from model.station import Type
from settings import config

neutral_percent = None
city_percent = None
activity_and_residential_percent = None
activity_and_residential_fluctuation = None


def load():
    global neutral_percent
    global city_percent
    global activity_and_residential_percent
    global activity_and_residential_fluctuation
    neutral_percent = int(config.model['neutral_percent'])
    city_percent = int(config.model['city_percent'])
    activity_and_residential_percent = int(config.model['activity_and_residential_percent'])
    activity_and_residential_fluctuation = int(config.model['activity_and_residential_fluctuation'])

    if activity_and_residential_fluctuation < 0 or activity_and_residential_fluctuation >= activity_and_residential_percent:
        activity_and_residential_fluctuation = round(activity_and_residential_percent / 2)


def convert_seconds(seconds):
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return '%02d:%02d:%02d' % (hours, minutes, secs)


def convert_to_exact_hour(seconds):
    return round(seconds / 3600, 2)


# noinspection PyTypeChecker
def station_probability(station, second, is_arrival=True):
    if neutral_percent is None or city_percent is None or activity_and_residential_percent is None or activity_and_residential_fluctuation is None:
        logging.error("Converter hasn't been loaded")
        return 0

    second = second % 86400
    station_type = station.station_type
    result = 0
    if station_type == Type.NEUTRAL:
        result = neutral_percent
    if station_type == Type.CITY:
        result = city_percent
    # TODO Change calculation for Activity and Residential
    if station_type == Type.ACTIVITY:
        if is_arrival:
            if second < 43200:
                result = activity_and_residential_percent + 50 * scipy.stats.norm.pdf(convert_to_exact_hour(second), 8, 1)
            else:
                result = activity_and_residential_percent - 50 * scipy.stats.norm.pdf(convert_to_exact_hour(second), 18, 1)
        else:
            if second < 43200:
                result = activity_and_residential_percent - 50 * scipy.stats.norm.pdf(convert_to_exact_hour(second), 8, 1)
            else:
                result = activity_and_residential_percent + 50 * scipy.stats.norm.pdf(convert_to_exact_hour(second), 18, 1)
    if station_type == Type.RESIDENTIAL:
        if is_arrival:
            if second < 43200:
                result = activity_and_residential_percent - 50 * scipy.stats.norm.pdf(convert_to_exact_hour(second), 8, 1)
            else:
                result = activity_and_residential_percent + 50 * scipy.stats.norm.pdf(convert_to_exact_hour(second), 18, 1)
        else:
            if second < 43200:
                result = activity_and_residential_percent + 50 * scipy.stats.norm.pdf(convert_to_exact_hour(second), 8, 1)
            else:
                result = activity_and_residential_percent - 50 * scipy.stats.norm.pdf(convert_to_exact_hour(second), 18, 1)
    return round(result / 100, 2)
