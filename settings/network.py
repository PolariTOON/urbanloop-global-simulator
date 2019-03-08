import json
import sys

import numpy as np

from model import capsule as model_capsule
from model import loop as model_loop
from model import station as model_station
from model import switch as model_switch
from model import warehouse as model_warehouse
from settings import simlog, config

"""
fichier pour l'import des réseaux sur les formats json correspondant
"""

_size = {}  # {'min_x': 0, 'max_x': 0, 'min_y': 0, 'max_y': 0}


def load(file_path=None):
    """
    fonction qui a partir d'un fichier json récupère le réseau correspondant et le traduit en objets
        :param file_path: fichier json (Par défaut il charge celui contenu dans settings/conf.ini)
        :return: (void) l'ensemble des objets sont créés et configurés.
    """
    if file_path is None:  # aller chercher celui par défaut
        file_path = '{0}/../resources/mini_network.json'.format(sys.path[0])

    model_loop.all_loops = {}  # autrement ca foire quand on charge un autre network
    with open(file_path, 'r') as file:
        network = json.load(file)
    for loop, info in network.items():
        # the_loop = None
        if loop in model_loop.all_loops:
            the_loop = model_loop.get_by_name(loop)
            the_loop.x = info["center"][0]
            the_loop.y = info["center"][1]
            the_loop.size = info["circonference"]
        else:
            the_loop = model_loop.Loop(loop, info["circonference"], info["center"])
        elms = []
        e = -1
        for element in info["content"]:
            e += 1
            el_type = element["type"]
            if el_type == "station":
                elms += [model_station.Station(name=element["name"], capacity=element["capacity"], loop=the_loop,
                                               angle=element["angle"], station_type=element["station_type"])]
                # the_loop.stations += [elms[e]]
            elif "switch" in el_type:
                other = element["other_loop"]
                if other in model_loop.all_loops:
                    other_l = model_loop.get_by_name(other)
                else:
                    other_l = model_loop.Loop(other)

                if el_type == "switch_out":
                    if other_l.switches is not None:
                        for s in other_l.switches:
                            if s.my_loop is the_loop and s.other_loop is other_l:  # il existe déjà
                                elms += [s]
                    if len(elms) != e + 1:  # existe pas
                        elms += [model_switch.Switch(loop=the_loop, other_loop=other_l)]
                    elms[e].angle_my_loop = element["angle"]
                    elms[e].size = element["length"]
                else:  # "switch_in":
                    if other_l.switches is not None:
                        for s in other_l.switches:
                            if s.my_loop is other_l and s.other_loop is the_loop:
                                elms += [s]
                    if len(elms) != e + 1:  # existe pas
                        elms += [model_switch.Switch(loop=other_l, other_loop=the_loop)]
                    elms[e].angle_other_loop = element["angle"]
                # the_loop.switches += [elms[e]]
            elif el_type == "warehouse":
                elms += [model_warehouse.Warehouse(loop=the_loop, angle=element["angle"], capacity=element["capacity"])]
            else:
                simlog.error("The json file is not properly formatted. "
                             "\n FORMAT : "
                             "\n \t { <loop_name(String)> : { "
                             "\n \t \t 'center'': [<x(int)>,<y(int)>], 'circonference': <size(int)>, "
                             "\n \t \t 'content': [ {'type':<'station'/'switch_out'/'switch_in'>, ..., "
                             "'angle':<clockwise, 0 on the top(int[0,359)>}"
                             "\n \t \t \t {'type':'station','name':<station_name(String)>,'station_type': "
                             "<visitation(int[1-3])>, 'capacity': <number_slot(int[2-inf],default=4)>, "
                             "'angle':<placing(int[0,359)>}, "
                             "\n \t \t \t {'type':'switch_out','other_loop':<loop_name(String)>, 'length': <size("
                             "int)>, 'angle':<placing(int[0,359)>}, "
                             "\n \t \t \t {'type':'switch_in','other_loop':<loop_name(String)>, 'angle':<placing(int["
                             "0,359)>} "
                             "\n \t ]}}")
        order = []
        the_loop.clockwise = info["clockwise"]
        tri_bulle(elms, the_loop)
        the_loop.add_order(elms)
        global _size
        radius = (the_loop.size / (2 * np.pi)) + 10
        # print(radius)
        if _size == {}:
            _size['min_x'] = the_loop.x - radius
            _size['max_x'] = the_loop.x + radius
            _size['min_y'] = the_loop.y - radius
            _size['max_y'] = the_loop.y + radius
        else:
            if the_loop.x - radius < _size['min_x']:
                _size['min_x'] = the_loop.x - radius
            elif the_loop.x + radius > _size['max_x']:
                _size['max_x'] = the_loop.x + radius
            if the_loop.y - radius < _size['min_y']:
                _size['min_y'] = the_loop.y - radius
            elif the_loop.y + radius > _size['max_y']:
                _size['max_y'] = the_loop.y + radius

    model_switch.init()
    '''nb_st = len(st.get_stations())
        print(nb_st)
        r = np.random.randint(nb_st)
        departure = st.get_station_by_id(r)
        r = np.random.randint(nb_st)
        arrivee = st.get_station_by_id(r)
        Traveler(departure.name, arrivee.name, 0)
        departure.capsule_queue.put(Capsule(departure))
        '''
    capsules = int(config.routing['number_of_capsules'])
    for i in range(6):
        for station in model_station.get_stations():
            if station.capsule_queue.qsize() < min(station.capacity - 1, 2) and capsules > 0:
                # creating capsules
                caps = model_capsule.Capsule(departure_station=station)
                # adding capsules to station
                station.capsule_queue.put(caps)
                capsules -= 1
    while capsules > 0:
        for warehouse in model_warehouse.get_warehouses():
            if capsules > 0 and warehouse.capsule_queue.qsize() < warehouse.capacity and capsules > 0:
                caps = model_capsule.Capsule(departure_station=warehouse)
                warehouse.capsule_queue.put(caps)
                capsules -= 1

    print(get_size())
    return


def reload(file_path=None):
    model_loop.all_loops = {}
    model_capsule._capsules = list()
    load(file_path)


def get_size():
    """
    :return: largeur ou longueur nécessaire pour afficher tout le réseau (contenu dans un carré)
    """
    global _size
    length = _size['max_x'] - _size['min_x']
    width = _size['max_y'] - _size['min_y']
    return max(length, width)


def tri_bulle(tab_objects, the_loop):
    to_permute = True
    cursor = 0
    angles = []
    for elm in tab_objects:
        # choix de l'angle
        if type(elm) is model_switch.Switch:
            if elm.my_loop is the_loop:
                angles.append(elm.angle_my_loop)
            else:
                angles.append(elm.angle_other_loop)
        else:
            angles.append(elm.angle)
    while to_permute :
        to_permute = False
        cursor += 1
        for i in range(0, len(tab_objects)-cursor):
            if angles[i] < angles[i+1] and not the_loop.clockwise:
                to_permute = True
                angles[i], angles[i+1] = angles[i+1], angles[i]
                tab_objects[i], tab_objects[i + 1] = tab_objects[i + 1], tab_objects[i]
            if angles[i] > angles[i+1] and the_loop.clockwise:
                to_permute = True
                angles[i], angles[i+1] = angles[i+1], angles[i]
                tab_objects[i], tab_objects[i + 1] = tab_objects[i + 1], tab_objects[i]
    return tab_objects
