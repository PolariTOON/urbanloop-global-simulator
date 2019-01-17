import sys
import json

from model import loop as ML
from model import switch as MS
from model.loop import Loop
from model.station import Station
from model.switch import Switch
from settings import config


def load():
    path_to_add_array = sys.path[0].split("/")
    del path_to_add_array[len(path_to_add_array)-1]
    path="/".join(path_to_add_array)
    path += config.model['network_file']
    f = open(path, 'r')
    network = json.load(f)
    for loop, info in network.items():
        # l = None
        if loop in ML.all_loops:
            l = ML.get_by_name(loop)
            l.x = info["center"][0]
            l.y = info["center"][1]
            l.size = info["circonference"]
        else:
            l = Loop(loop, info["circonference"], info["center"])
        elms = []
        e = -1
        for element in info["content"]:
            e += 1
            el_type = element["type"]
            if el_type == "station":
                elms += [Station(element["name"], None, l, element["angle"], element["station_type"])]
                l.stations += [elms[e]]
            elif "switch" in el_type:
                other = element["other_loop"]
                if other in ML.all_loops:
                    other_l = ML.get_by_name(other)
                else:
                    other_l = Loop(other)

                if el_type == "switch_out":
                    if other_l.switches is not None:
                        for s in other_l.switches:
                            if s.my_loop is l and s.other_loop is other_l:  # il existe déjà
                                elms += [s]
                    if len(elms) != e + 1:  # existe pas
                        elms += [Switch(l, other_l)]
                    elms[e].angle_my_loop = element["angle"]
                    elms[e].size = element["length"]
                else:  # "switch_in":
                    if other_l.switches is not None:
                        for s in other_l.switches:
                            if s.my_loop is other_l and s.other_loop is l:
                                elms += [s]
                    if len(elms) != e + 1:  # existe pas
                        elms += [Switch(other_l, l)]
                    elms[e].angle_other_loop = element["angle"]
                l.switches += [elms[e]]
            else:
                print("error")
            # print(elms[e])
        order = []
        for i in range(len(elms)):
            elm = elms[i]
            if type(elm) == Switch and elm.other_loop == l:
                elm.next_station_other = search_next_station(elms, i)
                order += [["switch_in", elm, elm.angle_other_loop]]
            else:  # type(elm) == Station or (type(elm) == Switch and elm.my_loop == l):
                elm.next_station = search_next_station(elms, i)
                elm.previous_station = search_previous_station(elms, i)
                if type(elm) == Station:
                    elm.next_switch = search_next_switch(elms, i, l)
                    order += [["station", elm, elm.angle]]
                else:
                    order += [["switch_out", elm, elm.angle_my_loop]]
        # print(elms)
        l.add_order(order)
    # print(ML.all_loops)
    MS.init()


def search_next_station(elements, i):
    length = len(elements)
    for index in range(length):
        e = elements[(index + i) % length]
        if type(e) == Station:
            return e


def search_previous_station(elements, i):
    length = len(elements)
    for index in range(length):
        e = elements[(index - i) % length]
        if type(e) == Station:
            return e


def search_next_switch(elements, i, loop):
    length = len(elements)
    for index in range(length):
        e = elements[(index + i) % length]
        if type(e) == Switch:
            if e.my_loop == loop:
                return e
