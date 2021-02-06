from numpy import floor
from random import seed, randint, random, choice
from model.entities.tokens.traveler import Traveler
import math
import numpy.random as np_rand

from model.entities.nodes.networks.ways.tracks import station


class Probability:
    """
    Modélise la probabilité d'apparition d'un voyageur dans une gare
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
        sum_coefficient = int(sum(peak_hours_coefficient))  # total des coefficients
        travelers_per_day = int(traveler["travelers_per_day"])  # on récupère le nombre moyen de voyageurs par jour
        traveler_lambda_per_hour = [travelers_per_day * coefficient / sum_coefficient for coefficient in peak_hours_coefficient]  # liste du nombre de passagers générés pour chaque heure de la journée
        self.traveler_per_tick = [traveler0 / (3600 / tick) for traveler0 in traveler_lambda_per_hour]  # nombre moyen de passagers générés par tick selon l'heure
        coef_station = []
        
        """
            - zone d’activité : 0
            - zone résidentielle : 1
            - ville : 2
        """
        for station0 in self.stations:
            if station0._station_type == 0:
                coef_station.append(0.1)
            elif station0._station_type == 1:
                coef_station.append(0.3)
            else:
                coef_station.append(0.5)
        tot_coef = sum(coef_station)
        for i in range(len(coef_station)):
            coef_station[i] = coef_station[i]/tot_coef
        self.coef_station = coef_station       # répartition des voyageurs dans le réseau

    def normal_law_density(x, mu=0, sigma=1):
        """
            Return the probability density function value for a normal law.
            
            @param x: position where the function is evaluated
            @param mu: mean
            @param sigma: standard deviation
        """
        sqrt = math.sqrt 
        pi, e = math.pi, math.e
        return 1 / (sigma * sqrt(2*pi)) * e ** (-0.5 * ((x-mu)/sigma) ** 2)
    
    def station_probability(self, station_type, second, is_arrival=True):
        """
        This function gives you the probability to lead a traveler to a station_type
        at a certain time in second. You can chose if the station is a departure or
        a destination station.
        :param station_type: The type of station you want to find its probability
        :param second: The time in second
        :param is_arrival: If the station is a departure or destination station
        :return: The probability to lead a traveler to the chosen station_type at the given time
        """
        second = second % 86400
        gaussian_factor = 250 * (self._activity_and_residential_fluctuation / 100)
        result = 0
        decimal_hour = round(second / 3600, 2)
        norm_mph = normal_law_density(decimal_hour, self._morning_peak_hour, 1)
        norm_eph = normal_law_density(decimal_hour, self._evening_peak_hour, 1)
        if station_type == station.station_types["city"]:
            result = self._city_percent
        if station_type == station.station_types["activity"]:
            if is_arrival:
                if second < 43200: # 43200s = 12h00
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

    """
      Remarque :
        - `generate_traveler_poisson()` :
            la loi de Poisson est utilisée pour obtenir le nombre nombre de voyageurs créés
            dans l'ensemble du réseau, puis ceux-ci sont répartis sur les stations.
        - `generate_traveler_2()` :
            la loi de Poisson est utilisée une fois pour chaque station, pour obtenir le
            nombre de voyageurs à y générer. Le nombre moyen de voyageurs sur l'ensemble du
            réseau reste cependant le même qu'avec `generate_traveler_poisson()`.
    """

    # todo - trouver comment corriger cette fonction,
    #  je n'ai pas eu le temps de comprendre j'ai refait une autre fonction
    def generate_traveler_poisson(self, boarding_time, time, env):
        """
        genere des voyageurs de manière aléatoire à chaque tick
        :param traveler_per_hour: number of traveler per day
        :param hour: The hour at which you want to create a traveler
        :param tick_per_second : number of tick per second
        :return: amount of generated traveler (0 or 1).
        """
        hour = int(round(time / 3600, 2)) % 24
        prob = 1 - math.exp(-self.traveler_per_tick[hour])
        if random() <= prob:
            ri = randint(1, len(self.stations))
            s = self.stations[ri - 1]
            r = random()
            if r <= self.station_probability(s.station_type, time, False):  # si le nombre aléatoire généré est inférieur à la probabilité d'appartion
                # pass
                traveler_source = s.name                    # la source est là où le traveler est généré
                self.statistiques.add_waiting_traveler(s.name)
                stations = []
                for station0 in self.stations:
                    stations.append(station0.name)
                stations.remove(s.name)
                traveler_destination = choice(stations)     # la destination une des autres stations
                s.travelers.append(Traveler(env, time, source=traveler_source, destination=traveler_destination, boarding_time=boarding_time))  # alors un voyageur est généré
                """print("\u001B[32mNew Traveler", "\u001B[0m", traveler_source, "\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t(simulation l.123)",
                                        "\n\t\t\u001B[32m|\u001B[0m nombre de travelers dans la station:", len(s.travelers),
                                        "\n\t\t\u001B[32m|\u001B[0m taille de la station:", s.capacity, "\n")"""
                s._all_time_count += 1

    def generate_traveler_2(self, time, env, state, boarding_time, nb_ticks=1):
        """utilisation de la loi de Poisson"""
        hour = int(round(time / 3600, 2)) % 24
        travelers_to_generate = nb_ticks * self.traveler_per_tick[hour]  # nb de voyageurs que l'on génère au tick présent
                                                                         # (ou au groupe de ticks présent si nb_ticks > 1)
        seed(state+12345)
        np_rand.seed((int(state)+123456) % 2**32) # 'seed' must receive a number between 0 and 2**32 - 1 (also, 123456 cas be any number)
        travelers_to_generate_per_station = []
        for coef0 in self.coef_station:
            travelers_to_generate_per_station.append(coef0*travelers_to_generate)   # répartition des passagers à générer selon le type de station
        for i_station in range(len(self.stations)):     # pour chaque station on génère ou non des voyageurs
            station0 = self.stations[i_station]
            for i_traveler in range(np_rand.poisson(travelers_to_generate_per_station[i_station], 1)[0]):  # génération selon une loi de poisson
                # get random destination
                if len(self.coef_station) > 1:
                    destination = self.get_rand_station()
                    while destination == station0:
                        destination = self.get_rand_station()
                else:
                    destination = station0
                # add traveler
                self.statistiques.add_waiting_traveler(station0.name)
                station0.travelers.append(Traveler(env, time, source=station0.name, destination=destination.name, boarding_time=boarding_time))
                station0.up_all_time_count()

    def get_rand_station(self):
        rand_x = random()
        station = None
        i = 0
        for j in range(len(self.coef_station)):
            i += self.coef_station[j]
            if i > rand_x:
                station = self.stations[j]
                break
        return station
