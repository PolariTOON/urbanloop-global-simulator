import glob
import json
import os
import sys

import numpy as np

from model import capsule as model_capsule
from model import identifier
from model import loop as model_loop
from model import station as model_station
from model import switch as model_switch
from model import traveler
from model import warehouse as model_warehouse
from settings import simlog, config

"""
fichier pour l'import des réseaux sur les formats json correspondant
"""

_size = {}  # {'min_x': 0, 'max_x': 0, 'min_y': 0, 'max_y': 0}
_added_signal = False
_removed_signal = False
_default_changed_signal = False


def load(file_name=None):
    """
    fonction qui a partir d'un fichier json récupère le réseau correspondant et le traduit en objets
        :param file_name: Nom du fichier json (Par défaut il charge celui contenu dans settings/conf.ini)
        :return: (void) l'ensemble des objets sont créés et configurés.
    """

    file_path = ('{0}/../resources/networks/default/' + get_default_file_name() + '.json').format(sys.path[0])
    if file_name is not None:
        if '.json' not in file_name:
            file_name += '.json'
        file_path = ('{0}/../resources/networks/' + file_name).format(sys.path[0])

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
                    # elms[e].size = element["length"]
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
        sections_loop(the_loop)
        global _size
        radius = (the_loop.size / (2 * np.pi)) + 10
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
    init_capsules()
    file.close()
    return


def reload(file_name=None):
    global _size
    _size = {}
    model_loop.all_loops = {}
    model_switch._switches = []
    model_switch.alive_timers = []
    model_warehouse._warehouses = list()
    model_station._stations = list()
    model_capsule._capsules = list()
    traveler.total_generated = 0
    identifier._loop_id = -1
    identifier._warehouse_id = -1
    identifier._station_id = -1
    identifier._switch_id = -1
    identifier._capsule_id = -1
    identifier._traveler_id = -1
    load(file_name)


def init_capsules():
    model_capsule._capsules = list()
    identifier._capsule_id = -1
    nb_capsules = int(config.capsule['number_of_capsules'])
    if nb_capsules == -1:  # infini = on rempli toutes les stations et entrepôts à capacity-1
        nb_capsules = sum([(a_station.capacity - 1) for a_station in model_station.get_stations()]
                          + [(a_warehouse.capacity - 1) for a_warehouse in model_warehouse.get_warehouses()])
    for i in range(6):
        for station in model_station.get_stations():
            if station.capsule_queue.qsize() < max(station.capacity - 1, 2) and nb_capsules > 0:
                # creating capsules
                caps = model_capsule.Capsule(departure_station=station)
                # adding capsules to station
                station.capsule_queue.put(caps)
                nb_capsules -= 1
    while nb_capsules > 0:
        for warehouse in model_warehouse.get_warehouses():
            if warehouse.capsule_queue.qsize() < warehouse.capacity - 1 and nb_capsules > 0:
                caps = model_capsule.Capsule(departure_station=warehouse)
                warehouse.capsule_queue.put(caps)
                nb_capsules -= 1


def get_size():
    """
    :return: largeur ou longueur nécessaire pour afficher tout le réseau (contenu dans un carré)
    """
    global _size
    # print(_size)
    length = _size['max_x'] - _size['min_x']
    width = _size['max_y'] - _size['min_y']
    return max(length, width)


def sections_loop(the_loop):
    """
    découpe la loop en sections entre 2 switchs
    :return: entre les éléments
    """
    switch1 = the_loop.switches[0]
    index_s = 1
    section = "%s_%d-%d" % (the_loop.name, switch1.id, the_loop.switches[index_s].id)
    # print(section, "\n \t", switch1.name)
    if switch1.my_loop is the_loop:  # switch_out
        switch1.section_my_loop = section
    else:
        switch1.section_other_loop = section
    index = the_loop.get_index_of(switch1)
    for j in range(1, len(the_loop.objects)):
        the_object = the_loop.objects[(index + j) % len(the_loop.objects)][1]
        # print('\t', the_object.name)
        if type(the_object) is model_station.Station or type(the_object) is model_warehouse.Warehouse:
            the_object.section_loop = section
        elif the_object is the_loop.switches[index_s]:
            index_s = (index_s + 1) % len(the_loop.switches)
            section = "%s_%d-%d" % (the_loop.name, the_object.id, the_loop.switches[index_s].id)
            # print('\n \n ', section, '\n \t', the_object.name )
            if the_object.my_loop is the_loop:
                # switch out
                the_object.section_my_loop = section
            else:
                # switch in
                the_object.section_other_loop = section

        else:
            simlog.error("ordre des switchs biaisés dans la boucle %s" % the_loop.name)


# def define_section(the_loop, switch1):
#     i = the_loop.switches.indexOf(switch1)
#     is_a_out = switch1.my_loop is the_loop
#     for j in range(1, len(the_loop.switches)):
#         index = (i+j)%len(the_loop.switches)
#         if is_a_out and the_loop.switches[index].other_loop is the_loop :
#             switch2 = the_loop.switches[index]
#             section =
#             switch1.section_my_loop =
#             return "%s_%d-%d" % (the_loop.name, switch1.id, switch2.id)
#         elif not is_a_out and the_loop.switches[index].my_loop is the_loop :
#             switch2 = the_loop.switches[index]
#             return "%s_%d-%d" % (the_loop.name, switch1.id, switch2.id)


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
    while to_permute:
        to_permute = False
        cursor += 1
        for i in range(0, len(tab_objects) - cursor):
            if angles[i] < angles[i + 1] and the_loop.clockwise:
                to_permute = True
                angles[i], angles[i + 1] = angles[i + 1], angles[i]
                tab_objects[i], tab_objects[i + 1] = tab_objects[i + 1], tab_objects[i]
            if angles[i] > angles[i + 1] and not the_loop.clockwise:
                to_permute = True
                angles[i], angles[i + 1] = angles[i + 1], angles[i]
                tab_objects[i], tab_objects[i + 1] = tab_objects[i + 1], tab_objects[i]
    return tab_objects


def get_network_json(file_name, is_default=False):
    if '.json' not in file_name:
        file_name += '.json'
    path = '{0}/../resources/networks/'.format(sys.path[0])
    if is_default:
        path = '{0}/../resources/networks/default/'.format(sys.path[0])
    with open(path + file_name) as network_file:
        return json.load(network_file)


def get_default_file_name():
    default_network_file_regex_path = '{0}/../resources/networks/default/*.json'.format(sys.path[0])
    default_network_file_paths = glob.glob(default_network_file_regex_path)
    if not default_network_file_paths:
        return
    default_network_file_path = default_network_file_paths[0]
    if os.sep in default_network_file_path and '.' in default_network_file_path.split(os.sep)[-1]:
        return default_network_file_path.split(os.sep)[-1].split('.')[0]


def get_network_file_names():
    network_file_regex_paths = '{0}/../resources/networks/*.json'.format(sys.path[0])
    network_file_paths = glob.glob(network_file_regex_paths)
    return [path.split(os.sep)[-1].split('.')[0] for path in network_file_paths if
            os.sep in path and '.' in path.split(os.sep)[-1]]


def add_network_file(file_name, network_json):
    global _added_signal

    if '.json' not in file_name:
        file_name += '.json'
    file_path = ('{0}/../resources/networks/' + file_name).format(sys.path[0])

    if not os.path.exists(file_path):
        with open(file_path, 'w') as new_network_json_file:
            json.dump(network_json, new_network_json_file, indent=4)
        new_network_json_file.close()
    _added_signal = True


def remove_network_file(file_name):
    global _removed_signal

    if '.json' not in file_name:
        file_name += '.json'
    file_path = ('{0}/../resources/networks/' + file_name).format(sys.path[0])
    if os.path.exists(file_path):
        os.remove(file_path)
    _removed_signal = True


def change_default_file(file_name):
    global _default_changed_signal

    if '.json' not in file_name:
        file_name += '.json'
    default_file_path = ('{0}/../resources/networks/default/' + get_default_file_name() + '.json').format(sys.path[0])
    file_path = ('{0}/../resources/networks/' + file_name).format(sys.path[0])
    new_default_file_path = default_file_path.replace('/default/', '/')
    new_file_path = file_path.replace(file_name, '/default/' + file_name)
    os.rename(default_file_path, new_default_file_path)
    os.rename(file_path, new_file_path)
    _default_changed_signal = True


def get_added_signal(reset=False):
    """
    :param reset: If reset, _added_signal = False
    :return: Returns a boolean indicating a network file has been added to network directory
    """
    global _added_signal
    if _added_signal and reset:
        _added_signal = False
        return True
    return _added_signal


def get_removed_signal(reset=False):
    """
    :param reset: If reset, _removed_signal = False
    :return: Returns a boolean indicating a network file has been removed from network directory
    """
    global _removed_signal
    if _removed_signal and reset:
        _removed_signal = False
        return True
    return _removed_signal


def get_default_changed_signal(reset=False):
    """
    :param reset: If reset, _removed_signal = False
    :return: Returns a boolean indicating a network file has been removed from network directory
    """
    global _default_changed_signal
    if _default_changed_signal and reset:
        _default_changed_signal = False
        return True
    return _default_changed_signal
