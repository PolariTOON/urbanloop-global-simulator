import logging

import scipy.stats

from model.station import Type
from settings import config

neutral_percent = 0
city_percent = 0
activity_and_residential_percent = 0
activity_and_residential_fluctuation = 0


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


def station_probability(station, second, is_arrival=True):
    if neutral_percent == 0 or city_percent == 0 or activity_and_residential_percent == 0 or activity_and_residential_fluctuation == 0:
        logging.error("Converter hasn't been loaded")
        return 0

    second = second % 86400
    station_type = station.type
    if station_type == Type.NEUTRAL:
        return round(neutral_percent / 100, 3)
    # TODO Change calculation for Activity and Residential
    if station_type == Type.ACTIVITY:
        if is_arrival:
            if second < 43200:
                return activity_and_residential_percent + 50 * scipy.stats.norm.pdf(convert_to_exact_hour(second), 8, 1)
            else:
                return activity_and_residential_percent - 50 * scipy.stats.norm.pdf(convert_to_exact_hour(second), 8, 1)
        else:
            if second < 43200:
                return activity_and_residential_percent - 50 * scipy.stats.norm.pdf(convert_to_exact_hour(second), 8, 1)
            else:
                return activity_and_residential_percent + 50 * scipy.stats.norm.pdf(convert_to_exact_hour(second), 8, 1)
    if station_type == Type.RESIDENTIAL:
        if is_arrival:
            if second < 43200:
                return activity_and_residential_percent - 50 * scipy.stats.norm.pdf(convert_to_exact_hour(second), 8, 1)
            else:
                return activity_and_residential_percent + 50 * scipy.stats.norm.pdf(convert_to_exact_hour(second), 8, 1)
        else:
            if second < 43200:
                return activity_and_residential_percent + 50 * scipy.stats.norm.pdf(convert_to_exact_hour(second), 8, 1)
            else:
                return activity_and_residential_percent - 50 * scipy.stats.norm.pdf(convert_to_exact_hour(second), 8, 1)
    if station_type == Type.CITY:
        return round(city_percent / 100, 3)
