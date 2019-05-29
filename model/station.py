import random
from enum import Enum
from math import floor

from model import capsule, controller
from model import identifier
from model import queue
from model import warehouse
from settings import simlog
from simulator import converter

from simulator import converter
from simulator import sim_loop
from settings import simlog

_stations = list()


class Type(Enum):
    ACTIVITY = 1
    RESIDENTIAL = 2
    CITY = 3


class Station:
    network = None

    def __init__(self, name=None, capacity=4, loop=None, angle=None, station_type=Type.CITY):
        """
        :param name: Name of the station
        :param capacity: Loop circumference (float)
        :param loop: Loop to which the station belongs
        :param angle: Angle between the top of the station and the position of the station - clockwise (float)
        :param station_type: Type of station compared to its affluence (Enum)
        """
        global _stations
        _stations.append(self)
        self.controller = controller.get_controller()
        self.uuid = identifier.generate_unique()
        self.id = identifier.generate_station_id()
        self.name = "Station #{0}".format(self.id) if (name is None) else name
        self.angle = angle
        self.capacity = capacity
        self.loop = loop
        self.station_type = station_type
        self.traveler_queue = queue.Queue()
        self.capsule_queue = queue.Queue(maxsize=capacity)
        self.next_element = None
        self.section_loop = None
        self.nb_to_send = 0
        self.capsule_arriving = False

    def reset_simulation(self):
        self.traveler_queue = queue.Queue()
        self.capsule_queue = queue.Queue(maxsize=self.capacity)

    def get_type(self):
        return (Type.ACTIVITY, Type.RESIDENTIAL, Type.CITY)[self.station_type - 1]

    def get_string_type(self):
        return ("Activity", "Residential", "City")[self.station_type - 1]

    def get_waiting_capsules_number(self):
        return self.capsule_queue.qsize()

    def get_waiting_travelers_number(self):
        return self.traveler_queue.qsize()

    def drain(self, destination=None):
        """
        This function will drain the first empty capsule if the station is 3/4 full.
        in order to make room for other capsules
        :param destination: The destination where the empty capsule should be sent
        """
        qsize = self.capsule_queue.qsize()
        '''if qsize < floor((3 * self.capacity) / 4):
            return'''
        for capsule_index in range(qsize):
            a_capsule = self.capsule_queue.get()
            if not a_capsule.is_aboard():
                if destination is None:
                    destination = get_almost_empty_station(self)
                a_capsule.destination = destination
                test = True

                for i in capsule.get_capsules():
                    if i.get_segment_trip_percentage() >= 90 and i.next_element == self:
                        test = False
                    if i.get_segment_trip_percentage() <= 10 and i.current_element == self:
                        test = False
                if test:
                    simlog.debug("Station %s (%s/%d capsules) drained to %s" % (
                    self.name, qsize, self.capacity, destination.name))
                    a_capsule.start_trip()
                return
            else:
                self.capsule_queue.put(a_capsule)

    def capsule_passing(self, capsule):
        self.controller = controller.get_controller()
        self.controller.update_from_switch(capsule)

    '''
    def complete(self):
        """
        This function will search to recover a capsule from a station 3/4 full.
        in order to make complete the queue
        """
        if self.capsule_queue.qsize() <= max(1, floor(self.capacity / 4)):
            departure = get_almost_full_station(destination_station=self)
            departure.drain(destination=self)
    '''

    def estimated_capsules_number(self):
        return self.capsule_queue.qsize() + len(capsule.get_incoming_capsule(self))

    def end_capsule_trip(self, capsule):
        self.controller.stop_timer(capsule)
        self.capsule_arriving = False


def get_stations():
    """
    :return: All stations of the network
    """
    return _stations


def fill_and_full_stations():
    """
    Appel le controleur pour completer la station. On considère que la station est en situation critique si il ne
    reste aucune capsule disponible. La demande est alors effectué avec une priorité maximale(1). La capsule vide
    sera donc autant prioritaire qu'une capsule pleine. Si il reste au moins une capsule alors la demande est
    effectué avec une priorité faible
    """
    simlog.debug("Stations drainage and completion process launched.")
    for station in get_stations():
        if station.estimated_capsules_number() <= max(1, floor(station.capacity / 4)):
            # quasi vide --> station à compléter
            simlog.debug(
                "Station %s almost empty (caps_numb = %d)." % (station.name, station.estimated_capsules_number()))
            nb_to_send = station.capacity - station.estimated_capsules_number() - 1
            if station.estimated_capsules_number() == 0 and not station.capsule_arriving :
                controller.get_controller().refill(10, station, nb_to_send)
                station.capsule_arriving = True
            elif station.capsule_arriving==False:
                controller.get_controller().refill(6,station,nb_to_send)
                capsule_arriving = True
                 # j'en envoie une depuis un entrepot
            """
            if nearer_warehouse is not None :
                nearer_warehouse.send_capsule(station)
                sim_loop.recorder.add_sent_capsules_drain(1, nearer_warehouse)
        # vérifier que la station n'est pas sujette à être la destination de plein de capsules
            proba = converter.station_probability(station.get_type(), now_second, True)
            if proba < 0.3 and nb_to_send>1 and nearer_warehouse is not None: # je ne prends pas trop de risque à en renvoyer d'autres
                for i in range(min(nb_to_send-1, 1)):
                    nearer_warehouse.send_capsule(station)
                    sim_loop.recorder.add_sent_capsules_drain(1, nearer_warehouse)
            """
        if station.estimated_capsules_number() >= min(station.capacity - 1, floor(3 * station.capacity /4)) and station.capsule_queue.qsize() > 1:
            # quasi pleine --> station à vider
            simlog.debug("Station %s almost full (caps_numb = %d, waiting travelers = %d)." % (
            station.name, station.estimated_capsules_number(), station.traveler_queue.qsize()))
            nb_to_send = 1
            if station.capsule_queue.qsize() > station.traveler_queue.qsize():
                nb_to_send = max(station.capsule_queue.qsize() - station.traveler_queue.qsize() - 1, 1)
            # j'en envoie une vide (si pas de voyageur) attente vers un entrepot
            controller.get_controller().drain(station)
            # station.drain(warehouse.which_warehouse_before(station(station)))


def get_station_by_name(name):
    """
    :param name: Name of the desired station
    :return: The desired station
    """
    global _stations
    for station in _stations:
        if station.name == name:
            return station


def get_almost_empty_station(departure_station=None):
    """
    :param departure_station: The departure_station
    :return: An almost empty station (3/4 empty). If there is no almost empty station,
    it will return a random station.
    """
    for station in random.sample(_stations, len(_stations)):
        if station not in (None, departure_station):
            if station.estimated_capsules_number() < max(1, floor(station.capacity / 4)):
                return station
    return random.choice(_stations)

'''
def get_almost_full_station(destination_station=None):
    """
    :param destination_station: The destination_station
    :return: An almost full station (3/4 full). If there is no almost full station,
    it will return a random station.
    """
    for station in random.sample(_stations, len(_stations)):
        if destination_station is not None and station is not destination_station:
            if station.estimated_capsules_number() > floor((3 * station.capacity) / 4):
                return station
    return random.choice(_stations)


def drain_all():
    """
    Drain every almost full stations, fill every almost empty stations
    """
    simlog.info("Stations drainage process launched.")
    for station in get_stations():
        if station.estimated_capsules_number() >= (station.capacity - 1):
            station.drain()
        if station.estimated_capsules_number() <= 1:
            station.complete()
'''



"""
def fill_and_full_stations():
    now_second = converter.now_to_seconds()
    # TODO unused variable -> now_hour = converter.seconds_to_floor_hour(now_second)
    simlog.debug("Stations drainage and completion process launched.")
    for station in get_stations():
        # print("type", station.get_type())
        if station.estimated_capsules_number() <= max(1, floor(station.capacity / 4)):
            # quasi vide --> station à compléter
            simlog.debug("Station %s almost empty (caps_numb = %d)." % (station.name, station.estimated_capsules_number()))
            nb_to_send = station.capacity - station.estimated_capsules_number() - 1
            nearer_warehouse = warehouse.which_warehouse_before(station)
            # j'en envoie une depuis un entrepot
            if nearer_warehouse is not None :
                nearer_warehouse.send_capsule(station)
                sim_loop.recorder.add_sent_capsules_drain(1, nearer_warehouse)
            # vérifier que la station n'est pas sujette à être la destination de plein de capsules
            proba = converter.station_probability(station.get_type(), now_second, True)
            if proba < 0.3 and nb_to_send>1 and nearer_warehouse is not None: # je ne prends pas trop de risque à en renvoyer d'autres
                for i in range(min(nb_to_send-1, 1)):
                    nearer_warehouse.send_capsule(station)
                    sim_loop.recorder.add_sent_capsules_drain(1, nearer_warehouse)

        if station.estimated_capsules_number() >= min(station.capacity - 1, floor(3 * station.capacity /4)) and station.capsule_queue.qsize() > 1:
            # quasi pleine --> station à vider
            simlog.debug("Station %s almost full (caps_numb = %d, waiting travelers = %d)." % (station.name, station.estimated_capsules_number(), station.traveler_queue.qsize()))
            nb_to_send = 1
            if station.capsule_queue.qsize() > station.traveler_queue.qsize():
                nb_to_send = max(station.capsule_queue.qsize() - station.traveler_queue.qsize() - 1, 1)
            nearer_warehouse = warehouse.which_warehouse_after(station)
            # j'en envoie une vide (si pas de voyageur) attente vers un entrepot
            station.drain(nearer_warehouse)
            if nearer_warehouse is not None and station.traveler_queue.qsize() <= 1:
                station.drain(nearer_warehouse)
                sim_loop.recorder.add_called_capsules_drain(1, nearer_warehouse)
            # vérifier que la station n'est pas sujette à voir partir plein de voyageurs
            proba = converter.station_probability(station.get_type(), now_second, False)
            if proba > 0.3 and nb_to_send > 1 and nearer_warehouse is not None:
                for i in range(min(nb_to_send - 1, 1)):
                    nearer_warehouse.send_capsule(station)
                    sim_loop.recorder.add_sent_capsules_drain(1, nearer_warehouse)
"""


def reset_simulation():
    """
    This function will reset every stations of the network
    """
    for station in _stations:
        station.reset_simulation()
