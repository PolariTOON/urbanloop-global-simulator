"""
Cette classe sert à instencier un modèle probabiliste de génération des voyageurs avec une loi de poisson
"""
import random

import numpy as np
import scipy.stats

from controler import converter
from model.networks.ways.tracks.station import Type
from settings import simlog


class Probability:
    def __init__(self, traveler, prob):
        self.city_percent = int(prob['city_percent'])
        self.activity_and_residential_percent = int(prob['activity_and_residential_percent'])
        self.activity_and_residential_fluctuation = int(prob['activity_and_residential_fluctuation'])
        self.ascent_descent_duration = int(traveler['ascent_descent_duration'])
        self.morning_peak_hour = int(traveler['morning_peak_hour'])
        self.evening_peak_hour = int(traveler['evening_peak_hour'])
        if self.activity_and_residential_fluctuation < 0 or self.activity_and_residential_fluctuation >= self.activity_and_residential_percent:
            self.activity_and_residential_fluctuation = np.floor(self.activity_and_residential_percent / 2)

    def random_ascent_descent_duration(self, tick_per_second):
        """
        :param tick_per_second: number of tick per second of the simulation
        :return: A value between [|time-2, time+2|]. time is the defined duration (in the config file)
        for ascent and descent events.
        """
        random_seconds = random.randrange(self.ascent_descent_duration - 2, self.ascent_descent_duration + 2, 1)
        return random_seconds * tick_per_second

    def station_probability(self, station_type, second, is_arrival=True):
        """
        This function gives you the probability to lead a traveler to a station_type
        at a certain time in second. You can choose if the station is a departure or
        destination station.
        :param station_type: The type of station you want to find its probability
        :param second: The time in second
        :param is_arrival: If the station is a departure or destination station
        :return: The probability to lead a traveler to the chosen station_type at the given time
        """
        if None in (
                self.city_percent, self.activity_and_residential_percent, self.activity_and_residential_fluctuation):
            simlog.error("Converter hasn't been loaded")
            return 0

        second = second % 86400
        mph = self.morning_peak_hour
        eph = self.evening_peak_hour
        gaussian_factor = 250 * (self.activity_and_residential_fluctuation / 100)
        result = 0
        decimal_hour = converter.seconds_to_decimal_hour(second) # TODO : à revoir ?
        norm_mph = scipy.stats.norm.pdf(decimal_hour, mph, 1)
        norm_eph = scipy.stats.norm.pdf(decimal_hour, eph, 1)
        if station_type == Type.CITY:
            result = self.city_percent
        if station_type == Type.ACTIVITY:
            if is_arrival:
                if second < 43200:
                    result = self.activity_and_residential_percent + gaussian_factor * norm_mph
                else:
                    result = self.activity_and_residential_percent - gaussian_factor * norm_eph
            else:
                if second < 43200:
                    result = self.activity_and_residential_percent - gaussian_factor * norm_mph
                else:
                    result = self.activity_and_residential_percent + gaussian_factor * norm_eph
        if station_type == Type.RESIDENTIAL:
            if is_arrival:
                if second < 43200:
                    result = self.activity_and_residential_percent - gaussian_factor * norm_mph
                else:
                    result = self.activity_and_residential_percent + gaussian_factor * norm_eph
            else:
                if second < 43200:
                    result = self.activity_and_residential_percent + gaussian_factor * norm_mph
                else:
                    result = self.activity_and_residential_percent - gaussian_factor * norm_eph
        return round(result / 100, 2)


def generate_traveler_poisson(traveler_per_day, hour):
    """
    This function gives you the amount of travelers you would create
    at a given hour.
    The lambda parameter is calculated hour by hour. It represents
    the mean number of travelers in a second.
    :param traveler_per_day: number of traveler per day
    :param hour: The hour at which you want to create a traveler
    :return: The number of traveler you would create at the given hour.
    """
    peak_hours_coefficient = [1, 1, 1, 1, 2, 3, 3, 6, 8, 8, 7, 4, 5, 5, 4, 4, 6, 7, 8, 6, 4, 3, 2, 2]
    somme_coefficient = np.sum(peak_hours_coefficient)
    traveler_lambda_per_hour = [traveler_per_day * coefficient / (3600 * somme_coefficient) for coefficient in
                                peak_hours_coefficient]
    return np.random.poisson(traveler_lambda_per_hour[hour], 1)[0]
