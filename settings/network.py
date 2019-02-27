import json
import sys

from settings import simlog

from model import loop as model_loop
from model import switch as model_switch
from model import capsule as model_capsule
from model.loop import Loop
from model import station as model_station
from model.switch import Switch

"""
fichier pour l'import des réseaux sur les formats json correspondant
"""


def load(file_path=None):
    print("LOAD")
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
            the_loop = Loop(loop, info["circonference"], info["center"])
        elms = []
        e = -1
        for element in info["content"]:
            e += 1
            el_type = element["type"]
            if el_type == "station":
                elms += [model_station.Station(name=element["name"], capacity=element["capacity"], loop=the_loop,
                                               angle=element["angle"], station_type=["station_type"])]
                the_loop.stations += [elms[e]]
            elif "switch" in el_type:
                other = element["other_loop"]
                if other in model_loop.all_loops:
                    other_l = model_loop.get_by_name(other)
                else:
                    other_l = Loop(other)

                if el_type == "switch_out":
                    if other_l.switches is not None:
                        for s in other_l.switches:
                            if s.my_loop is the_loop and s.other_loop is other_l:  # il existe déjà
                                elms += [s]
                    if len(elms) != e + 1:  # existe pas
                        elms += [Switch(loop=the_loop, other_loop=other_l)]
                    elms[e].angle_my_loop = element["angle"]
                    elms[e].size = element["length"]
                else:  # "switch_in":
                    if other_l.switches is not None:
                        for s in other_l.switches:
                            if s.my_loop is other_l and s.other_loop is the_loop:
                                elms += [s]
                    if len(elms) != e + 1:  # existe pas
                        elms += [Switch(loop=other_l, other_loop=the_loop)]
                    elms[e].angle_other_loop = element["angle"]
                the_loop.switches += [elms[e]]
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
        for i in range(len(elms)):
            # gestion des elements precedents et suivants
            elm = elms[i]
            if type(elm) == Switch and elm.other_loop == the_loop:  # c'est un switch_in
                elm.next_element_other = elms[(i + 1) % len(elms)]
                order += [["switch_in", elm, elm.angle_other_loop]]
            else:  # type(elm) == Station or (type(elm) == Switch and elm.my_loop == l):
                elm.next_element = elms[(i + 1) % len(elms)]
                if type(elm) == Switch:
                    elm.previous_element = elms[(i - 1) % len(elms)]
                    order += [["switch_out", elm, elm.angle_my_loop]]
                else:
                    order += [["station", elm, elm.angle]]
        the_loop.add_order(order)
    model_switch.init()
    '''nb_st = len(st.get_stations())
        print(nb_st)
        r = np.random.randint(nb_st)
        departure = st.get_station_by_id(r)
        r = np.random.randint(nb_st)
        arrivee = st.get_station_by_id(r)
        Traveler(departure.name, arrivee.name, 0)
        departure.capsule_queue.put_nowait(Capsule(departure))
        '''
    for station in model_station.get_stations():
        for i in range(station.capacity):
            if station.capsule_queue.qsize() < (station.capacity - 1):
                # creating capsules
                caps = model_capsule.Capsule(departure_station=station)
                # adding capsules to station
                station.capsule_queue.put_nowait(caps)
    # print("load done")
    return


def reload(file_path=None):
    model_loop.all_loops = {}
    model_capsule._capsules = list()
    load(file_path)


'''
def search_next_station(elements, i):
    """
    recherche la première station juste après un élément parmis les éléments dans une boucle
        :param elements: liste des objets sur la boucle ([Stations/Switchs])
        :param  i: indice de l'élément dont on cherche la station suivante (int)
        :return: la station suivante (Station)
    """
    length = len(elements)
    for index in range(length):
        e = elements[(index + i) % length]
        if type(e) == Station:
            return e


def search_previous_station(elements, i):
    """
    recherche la première station juste avant un élément parmis les éléments dans une boucle
        :param elements: liste des objets sur la boucle ([Stations/Switchs])
        :param i: indice de l'élément dont on cherche la station précédente (int)
        :return: la station précédente (Station)
    """
    length = len(elements)
    for index in range(length):
        e = elements[(index - i) % length]
        if type(e) == Station:
            return e


def search_next_switch(elements, i, loop):
    """
    recherche le premier switch "out" après un élément parmis les éléments dans une boucle
        :param  elements: liste des objets sur la boucle ([Stations/Switchs])
        :param  i: indice de l'élément dont on cherche la station précédente (int)
        :param  loop: boucle dans laquelle on cherche (il faut que le switch soit dans la boucle et non pas que ce
                        soit un switch qui aiguille vers cette boucle) (Loop)
        :return: le switch suivant qui aiguille depuis la boucle choisie (Switch)
    """
    length = len(elements)
    for index in range(length):
        e = elements[(index + i) % length]
        if type(e) == Switch:
            if e.my_loop == loop:
                return e
'''
