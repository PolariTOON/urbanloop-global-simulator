from settings import config
import json
from model.loop import Loop
from model import loop as ML
from model.station import Station
from model.switch import Switch
from model import switch as MS


#  CONFIG_PATH = '../resources/config.ini'
# config.load(CONFIG_PATH)


def load(file):
    f = open(file, 'r')
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
                elms += [Station(element["name"], None, l, element["angle"])]
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
        # TODO parcours elms pour avoir les précédents, suivants et faire le tableau order = [noeud, angle]
        # print(elms)
    # print(ML.all_loops)
    MS.init()
