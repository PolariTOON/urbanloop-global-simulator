import random

import numpy as np
import scipy.stats

from model.entities.nodes.networks.ways.tracks import station


class Probability:
    """
    TODO : la génération de voyageur est à faire dans chaque gare en s'inspirant de la génération globale faite dans l'ancien simulateur
    Modélise la prbabilité d'apparition d'un voyageur dans une gare
    """

    def __init__(self, traveler, prob):
        self._city_percent = int(prob['city_percent'])
        self._activity_and_residential_percent = int(prob['activity_and_residential_percent'])
        self._activity_and_residential_fluctuation = int(prob['activity_and_residential_fluctuation'])
        self._ascent_descent_duration = int(traveler['ascent_descent_duration'])
        self._morning_peak_hour = int(traveler['morning_peak_hour'])
        self._evening_peak_hour = int(traveler['evening_peak_hour'])
        if self._activity_and_residential_fluctuation < 0 or self._activity_and_residential_fluctuation >= self._activity_and_residential_percent:
            self._activity_and_residential_fluctuation = np.floor(self._activity_and_residential_percent / 2)

    def random_ascent_descent_duration(self, tick_per_second):
        """
        :param tick_per_second: number of tick per second of the simulation
        :return: A value between [|time-2, time+2|]. time is the defined duration (in the config file)
        for ascent and descent events.
        """
        random_seconds = random.randrange(self._ascent_descent_duration - 2, self._ascent_descent_duration + 2, 1)
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
                self._city_percent, self._activity_and_residential_percent, self._activity_and_residential_fluctuation):
            print("Converter hasn't been loaded")
            return 0
        second = second % 86400
        gaussian_factor = 250 * (self._activity_and_residential_fluctuation / 100)
        result = 0
        decimal_hour = round(second / 3600, 2)
        norm_mph = scipy.stats.norm.pdf(decimal_hour, self._morning_peak_hour, 1)
        norm_eph = scipy.stats.norm.pdf(decimal_hour, self._evening_peak_hour, 1)
        if station_type == station.station_types["city"]:
            result = self._city_percent
        if station_type == station.station_types["activity"]:
            if is_arrival:
                if second < 43200:
                    result = self._activity_and_residential_percent + gaussian_factor * norm_mph
                else:
                    result = self._activity_and_residential_percent - gaussian_factor * norm_eph
            else:
                if second < 43200:
                    result = self._activity_and_residential_percent - gaussian_factor * norm_mph
                else:
                    result = self._activity_and_residential_percent + gaussian_factor * norm_eph
        if station_type == station.station_types["residential"]:
            if is_arrival:
                if second < 43200:
                    result = self._activity_and_residential_percent - gaussian_factor * norm_mph
                else:
                    result = self._activity_and_residential_percent + gaussian_factor * norm_eph
            else:
                if second < 43200:
                    result = self._activity_and_residential_percent + gaussian_factor * norm_mph
                else:
                    result = self._activity_and_residential_percent - gaussian_factor * norm_eph
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
    somme_coefficient = int(np.sum(peak_hours_coefficient))
    traveler_per_day = int(traveler_per_day)
    traveler_lambda_per_hour = [traveler_per_day * coefficient / (3600 * somme_coefficient) for coefficient in
                                peak_hours_coefficient]
    return max(np.random.poisson(traveler_lambda_per_hour[hour], 1)[0], 1)
