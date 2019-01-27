import queue
from enum import Enum

from .loop import all_loops

station_id = 0


class Type(Enum):
    NEUTRAL = 0
    ACTIVITY = 1
    RESIDENTIAL = 2
    CITY = 3


class Station:
    network = None

    def __init__(self, name=None, capacity=100, loop=None, angle=None, station_type=Type.NEUTRAL):
        """
        :param name: Name of the station
        :param capacity: Loop circumference (float)
        :param loop: Loop to which the station belongs
        :param angle: Angle between the top of the loop and the position of the station - clockwise (float)
        :param station_type: Type of station compared to its affluence (Enum)
        """
        global station_id
        self.id = station_id
        station_id += 1
        self.name = "Station #{0}".format(self.id) if (name is None) else name
        self.angle = angle
        self.capacity = capacity
        self.loop = loop
        self.station_type = station_type
        self.traveler_queue = queue.Queue()
        self.capsule_queue = queue.Queue(maxsize=100)
        self.next_element = None


def get_stations():
    """
    récupère toute les stations
        :return: tableau de toutes les stations toutes boucles confondues ([Station])
    """
    stations = []
    for name, loop in all_loops.items():
        for station in loop.stations:
            stations.append(station)
    return stations


def get_by_name(name):
    """
    :param name: Name of the desired station
    :return: The desired station
    """
    for station in get_stations():
        if station.name == name:
            return station
