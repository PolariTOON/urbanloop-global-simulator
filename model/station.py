#! /usr/bin/env python3
# coding: utf-8
from enum import Enum
from queue import Queue
from model.capsule import Capsule

from .loop import all_loops

station_id = 0


class Type(Enum):
    NEUTRAL = 0
    ACTIVITY = 1
    RESIDENTIAL = 2
    CITY = 3


class Station:
    # network
    network = None

    def __init__(self, name=None, capacity=100, loop=None, angle=None, station_type=Type.NEUTRAL):
        """
        initialisation d'une station
        :param name : Nom de la station
        :param capacity: Circonference de la boucle (float)
        :param loop : boucle à laquelle la station appartient (Loop)
        :param angle : angle entre le haut de la boucle et la position de la station - sens horaire (float)
        :param station_type : type de station par rapport à son affluence (Enum)
        :return:0UT : un objet Station (Station)
        """
        global station_id
        self.id = station_id
        station_id += 1
        self.name = "Station #{0}".format(self.id) if (name is None) else name
        self.angle = angle
        self.capacity = capacity
        self.loop = loop
        self.station_type = station_type
        self.traveler_queue = Queue()
        self.capsule_queue = Queue(maxsize=self.capacity)
        self.capsule_queue.put(Capsule(this))

    # TODO menage
    '''def _update_flow(self):
        print("updating flow of ", self.id, "...")
        return

    def show_details(self):
        print("showing details...")
        print("\n \t id = ", self.id, "\n \t name = ", self.name)
        return
    '''


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
    récupérer une station par rapport à son nom
        :param  name : le nom de la station voulue (String) OBLIGATOIRE
        :return: 0UT : la station voulue (Station)
    """
    for station in get_stations():
        if station.name == name:
            return station
