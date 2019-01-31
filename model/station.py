import queue
from enum import Enum

_stations = list()
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
        self.capsule_queue = queue.Queue(maxsize=100)
        self.next_element = None


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
