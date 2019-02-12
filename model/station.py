import logging
import queue
from enum import Enum
import random

from model import capsule

_stations = list()
station_id = 0


class Type(Enum):
    NEUTRAL = 0
    ACTIVITY = 1
    RESIDENTIAL = 2
    CITY = 3


class Station:
    network = None

    def __init__(self, name=None, capacity=4, loop=None, angle=None, station_type=Type.NEUTRAL):
        """
        :param name: Name of the station
        :param capacity: Loop circumference (float)
        :param loop: Loop to which the station belongs
        :param angle: Angle between the top of the loop and the position of the station - clockwise (float)
        :param station_type: Type of station compared to its affluence (Enum)
        """
        global station_id
        global _stations
        self.id = station_id
        station_id += 1
        _stations.append(self)
        self.name = "Station #{0}".format(self.id) if (name is None) else name
        self.angle = angle
        self.capacity = capacity
        self.loop = loop
        self.station_type = station_type
        self.traveler_queue = queue.Queue()
        self.capsule_queue = queue.Queue(maxsize=capacity)
        self.next_element = None

    def reset_simulation(self):
        self.traveler_queue = queue.Queue()
        self.capsule_queue = queue.Queue(maxsize=self.capacity)

    def show_details(self):
        """
        crée un text contenant toutes les informations à propos de la station
        :return: String
        """
        details = "Station name : " + self.name
        details += "\nStation id : " + str(self.id)
        details += "\nLoop : " + self.loop.name
        details += "\nStation Type : "
        t = self.station_type
        if t == 0:
            details += "neutral"
        elif t == 1:
            details += "activity zone"
        elif t == 2:
            details += "residential zone"
        elif t == 3:
            details += "down town"
        details += "\nCapacity : " + str(self.capacity)
        details += "\nNext element : "
        if type(self.next_element) is Station:
            details += "Station " + self.next_element.name
        else:
            details += "Switch " + str(self.next_element.id)
        if self.capsule_queue.qsize() != 0:
            details += "\nCapsules (%d): " % self.capsule_queue.qsize()
            l = list(self.capsule_queue.queue)
            for c in l:
                details += "\n    Capsule #{0}".format(c.id)
        return details

    def drain(self):
        """
        Lance les capsules vides dans le réseau si la station est trop pleine
        :return:
        """
        if self.capsule_queue.qsize() >= round((3 * self.capacity) / 4):
            empty = 0
            for caps in list(self.capsule_queue.queue):
                if not caps.is_aboard():
                    empty += 1
                    if empty >= 2:
                        # la lancer
                        dest = get_almost_empty_station(self)
                        logging.debug(str(dest.loop))
                        caps.destination = dest
                        caps.start_trip()


def get_stations():
    """
    :return: All stations of the network
    """
    return _stations


def get_station_by_name(name):
    """
    :param name: Name of the desired station
    :return: The desired station
    """
    global _stations
    for station in _stations:
        if station.name == name:
            return station


def reset_simulation():
    """
    This function will reset every stations of the network
    """
    for station in _stations:
        station.reset_simulation()
        station.capsule_queue.put(capsule.Capsule(departure_station=station))
        station.capsule_queue.put(capsule.Capsule(departure_station=station))


def get_almost_empty_station(departure_station=None):
    """
    :param departure_station: The departure_station
    :return: An almost empty station (2/3 empty). If there is no almost empty station,
    it will return a random station.
    """
    for station in random.sample(_stations, len(_stations)):
        if departure_station is not None and station is departure_station:
            continue
        if station.capsule_queue.qsize() < round(station.capacity / 3):
            return station

    return random.choice(_stations)
