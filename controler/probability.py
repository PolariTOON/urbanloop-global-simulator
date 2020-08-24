from numpy import floor, sum
from random import randint, random, choice
from model.entities.tokens.traveler import Traveler
from scipy.stats import norm
import math

from model.entities.nodes.networks.ways.tracks import station


class Probability:
    """
    Modélise la prbabilité d'apparition d'un voyageur dans une gare
    """

    def __init__(self, prob, traveler, stations, statistiques, tick):
        self._city_percent = int(prob['city_percent'])
        self._activity_and_residential_percent = int(prob['activity_and_residential_percent'])
        self._activity_and_residential_fluctuation = int(prob['activity_and_residential_fluctuation'])
        if None in (self._city_percent, self._activity_and_residential_percent, self._activity_and_residential_fluctuation):
            raise ValueError("Converter hasn't been loaded (probability l.20)")
        self._morning_peak_hour = int(traveler['morning_peak_hour'])
        self._evening_peak_hour = int(traveler['evening_peak_hour'])
        if self._activity_and_residential_fluctuation < 0 or self._activity_and_residential_fluctuation >= self._activity_and_residential_percent:
            self._activity_and_residential_fluctuation = floor(self._activity_and_residential_percent / 2)
        self.stations = stations
        self.statistiques = statistiques
        peak_hours_coefficient = [1, 1, 1, 1, 1, 1, 7, 40, 20, 15, 15, 10, 20, 20, 15, 7, 15, 20, 20, 10, 7, 3, 2, 2]  # coefficient de fréquentation selon l'heure de la journée
        somme_coefficient = int(sum(peak_hours_coefficient))  # total des coefficients
        travelers_per_day = int(traveler["travelers_per_day"])  # on récupère le nombre moyen de voyageurs par jour
        traveler_lambda_per_hour = [travelers_per_day * coefficient / somme_coefficient for coefficient in peak_hours_coefficient]  # liste du nombre de passagers générés pour chaque heure de la journée
        self.traveler_per_tick = [traveler0 / (3600 / tick) for traveler0 in traveler_lambda_per_hour]  # nombre moyen de passagers générés par tick selon l'heure

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
        second = second % 86400
        gaussian_factor = 250 * (self._activity_and_residential_fluctuation / 100)
        result = 0
        decimal_hour = round(second / 3600, 2)
        norm_mph = norm.pdf(decimal_hour, self._morning_peak_hour, 1)
        norm_eph = norm.pdf(decimal_hour, self._evening_peak_hour, 1)
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

    def generate_traveler_poisson(self, hour, time, env):
        """
        genere des voyageurs de manière aléatoire à chaque tick
        :param traveler_per_hour: number of traveler per day
        :param hour: The hour at which you want to create a traveler
        :param tick_per_second : number of tick per second
        :return: amount of generated traveler (0 or 1).
        """
        prob = 1 - math.exp(-self.traveler_per_tick[hour])
        if random() <= prob:
            ri = randint(1, len(self.stations))
            s = self.stations[ri - 1]
            r = random()
            # todo - trouver comment marche station_probability
            # todo comprendre le truc en dessous...
            # todo augmenter les chances d'aller vers une station plus fréquentée plutôt qu'un tirage au sort pour la destination

            if r <= self.station_probability(s.station_type, time, False):  # si le nombre aléatoire généré est inférieur à la probabilité d'appartion
                # pass
                traveler_source = s.name                    # la source est là où le traveler est généré
                self.statistiques.add_waiting_traveler(s.name)
                stations = []
                for station0 in self.stations:
                    stations.append(station0.name)
                stations.remove(s.name)
                traveler_destination = choice(stations)     # la destination une des autres stations
                s.travelers.append(Traveler(env, time, source=traveler_source, destination=traveler_destination))  # alors un voyageur est généré
                """print("\u001B[32mNew Traveler", "\u001B[0m", traveler_source, "\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t(simulation l.123)",
                                        "\n\t\t\u001B[32m|\u001B[0m nombre de travelers dans la station:", len(s.travelers),
                                        "\n\t\t\u001B[32m|\u001B[0m taille de la station:", s.capacity, "\n")"""
                s._all_time_count += 1