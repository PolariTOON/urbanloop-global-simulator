"""
Cette classe sert à instencier un modèle probabiliste de génération des voyageurs avec une loi de poisson
"""

import numpy as np
import scipy.stats

from controler import converter
from settings import simlog


def generate_traveler_poisson(traveler_per_day, hour):
    """
    This function gives you the amount of travelers you would create
    at a given hour.
    The lambda parameter is calculated hour by hour. It represents
    the mean number of travelers in a second.
    :param traveler_per_day: number of traveler per day TODO : ce paramètre est à prendre au début dans config.ini
    :param hour: The hour at which you want to create a traveler
    :return: The number of traveler you would create at the given hour.
    """
    peak_hours_coefficient = [1, 1, 1, 1, 2, 3, 3, 6, 8, 8, 7, 4, 5, 5, 4, 4, 6, 7, 8, 6, 4, 3, 2, 2]
    somme_coefficient = np.sum(peak_hours_coefficient)
    traveler_lambda_per_hour = [traveler_per_day * coefficient / (3600 * somme_coefficient) for coefficient in
                                peak_hours_coefficient]
    return np.random.poisson(traveler_lambda_per_hour[hour], 1)[0]

def station_probability(self, station_type, second, is_arrival=True):
    """
    TODO : A CHANGER DE PLACE, SERT A LA GENERATION DE VOYAGEURS
    This function gives you the probability to lead a traveler to a station_type
    at a certain time in second. You can choose if the station is a departure or
    destination station.
    :param station_type: The type of station you want to find its probability
    :param second: The time in second
    :param is_arrival: If the station is a departure or destination station
    :return: The probability to lead a traveler to the chosen station_type at the given time
    """
    if None in (self.city_percent, self.activity_and_residential_percent, self.activity_and_residential_fluctuation):
        simlog.error("Converter hasn't been loaded")
        return 0

    second = second % 86400
    mph = self.morning_peak_hour
    eph = self.evening_peak_hour
    gaussian_factor = 250 * (self.activity_and_residential_fluctuation / 100)
    result = 0
    if station_type == station.Type.CITY:
        result = self.city_percent
    if station_type == station.Type.ACTIVITY:
        if is_arrival:
            if second < 43200:
                result = self.activity_and_residential_percent + gaussian_factor * scipy.stats.norm.pdf(
                    converter.seconds_to_decimal_hour(second), mph, 1)
            else:
                result = self.activity_and_residential_percent - gaussian_factor * scipy.stats.norm.pdf(
                    converter.seconds_to_decimal_hour(second), eph, 1)
        else:
            if second < 43200:
                result = self.activity_and_residential_percent - gaussian_factor * scipy.stats.norm.pdf(
                    converter.seconds_to_decimal_hour(second), mph, 1)
            else:
                result = self.activity_and_residential_percent + gaussian_factor * scipy.stats.norm.pdf(
                    converter.seconds_to_decimal_hour(second), eph, 1)
    if station_type == station.Type.RESIDENTIAL:
        if is_arrival:
            if second < 43200:
                result = self.activity_and_residential_percent - gaussian_factor * scipy.stats.norm.pdf(
                    converter.seconds_to_decimal_hour(second), mph, 1)
            else:
                result = self.activity_and_residential_percent + gaussian_factor * scipy.stats.norm.pdf(
                    converter.seconds_to_decimal_hour(second), eph, 1)
        else:
            if second < 43200:
                result = self.activity_and_residential_percent + gaussian_factor * scipy.stats.norm.pdf(
                    converter.seconds_to_decimal_hour(second), mph, 1)
            else:
                result = self.activity_and_residential_percent - gaussian_factor * scipy.stats.norm.pdf(
                    converter.seconds_to_decimal_hour(second), eph, 1)
    return round(result / 100, 2)