import queue
import random
from enum import Enum

from settings import simlog

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
        # logging.debug(self.name + "'s capacity = "+ str(capacity))
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

    def drain(self, destination=None):
        """
        This function will drain the first empty capsule if the station is 3/4 full.
        in order to make room for other capsules
        """
        if self.capsule_queue.qsize() >= round((3 * self.capacity) / 4):
            compt = self.capsule_queue.qsize()
            # empty = 0
            for capsule_index in range(self.capsule_queue.qsize()):  # for a_capsule in self.capsule_queue.queue():
                a_capsule = self.capsule_queue.get_nowait()
                if not a_capsule.is_aboard():
                    # empty += 1
                    if True: # if empty > 2:
                        if destination is None:
                            destination = get_almost_empty_station(self)
                        a_capsule.destination = destination
                        simlog.debug("Station %s (%s/%d capsules) drained to "
                                     "%s (%d/%d capsules)" % (self.name, compt, self.capacity, destination.name,
                                                              destination.capsule_queue.qsize(), destination.capacity))
                        a_capsule.start_trip()
                        return
                else:
                    self.capsule_queue.put_nowait(a_capsule)

    def complete(self):
        """
        This function will search to recover a capsule from a station 3/4 full.
        in order to make complete the queue
        """
        if self.capsule_queue.qsize() <= max(1, round(self.capacity / 4)):
            departure = get_almost_full_station(self)
            departure.drain(self)


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
        station.capsule_queue.put_nowait(capsule.Capsule(departure_station=station))
        station.capsule_queue.put_nowait(capsule.Capsule(departure_station=station))


def get_almost_empty_station(departure_station=None):
    """
    :param departure_station: The departure_station
    :return: An almost empty station (3/4 empty). If there is no almost empty station,
    it will return a random station.
    """
    for station in random.sample(_stations, len(_stations)):
        if departure_station is not None and station is not departure_station:
            if station.capsule_queue.qsize() < max(1, round(station.capacity / 4)):
                return station
    return random.choice(_stations)


def get_almost_full_station(destination_station=None):
    """
    :param destination_station: The destination_station
    :return: An almost full station (3/4 full). If there is no almost full station,
    it will return a random station.
    """
    for station in random.sample(_stations, len(_stations)):
        if destination_station is not None and station is not destination_station:
            if station.capsule_queue.qsize() > round((3 * station.capacity) / 4) :
                return station
    return random.choice(_stations)


def drain_all():
    """ Vide l'ensemble des stations 'trop pleines' _ rempli les 'trop vides'"""
    for station in get_stations():
        if station.capsule_queue.qsize() >= (station.capacity - 1):
            station.drain()
        if station.capsule_queue.qsize() <= 1:
            station.complete()
