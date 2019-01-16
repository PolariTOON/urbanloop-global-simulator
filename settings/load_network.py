from settings import config
import json
from model.loop import Loop
from model import loop as ML
from model.station import Station
from model.switch import Switch
from model import switch as MS

CONFIG_PATH = '../resources/config.ini'
config.load(CONFIG_PATH)

f = open(str(config.model['network_file']), 'r')
network = json.load(f)
for loop, info in network.items():
    if loop in ML.all_loops:
        l = ML.get_by_name(loop)
        l.x = info["center"][0]
        l.y = info["center"][1]
    else :
        l = Loop(loop, info["center"])
    l.size = info["circonference"]
    elms = []
    e = -1
    for element in info["content"]:
        e += 1
        el_type = element["type"]
        if el_type == "station":
            print("s")
            elms += [Station(element["name"], None, element["angle"]), l]
            l.stations += [elms[e]]
        elif el_type == "switch_out":
            print("so")
            other = element["other_loop"]
            if other in ML.all_loops:
                other_l = ML.get_by_name(other)
            else:
                other_l = Loop(other)
            if other_l.switches is not None:
                for s in other_l.switches:
                    if s.my_loop is l and s.other_loop is other_l:
                        elms += [s]
                        s.angle_my_loop = element["angle"]
            # elms += [Switch(element["name"], None, element["angle"])]
            # l.switches += [elms[e]]
        elif el_type == "switch_in":
            print("si")
        else:
            print("error")

#print(ML.all_loops)