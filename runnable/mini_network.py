import logging

import model.loop as ML
from settings import network


"""fichier de test d'import d'un réseau """


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

network_path = '../resources/mini_network.json'
try:
    with open(network_path, "r") as file:
        None
except FileNotFoundError:
    network_path = 'resources/mini_network.json'


network.load(network_path)

# on charge toutes les boucles créées
for name, l in ML.all_loops.items():
    logging.info("\n" + l.name + ", circonférence : "+ str(l.size) + " coordonnées du centre : x = " + str(l.x) + ", y = " + str(l.y))
    logging.debug("\t Stations : " + str([[st.name, st.id] for st in l.stations]))
    logging.debug("\t  -- an object in the loop = [[nature, id, angle in the loop]] -- ")
    logging.debug("\t" + str([[o[0], o[1].id, o[2]] for o in l.objects]))  # objects est un attributs des loops qui contient la succession des éléments
    for sw in l.switches:
        if sw.my_loop == l:
            logging.info("\t \t table of switch " + str(sw.id) + " : " + str(sw.table))
    # logging.debug(l.lengths)

loop_nancy = ML.get_by_name("Nancy")
o = loop_nancy.objects[2][1]
dist, next_elm = loop_nancy.dist_to_next_object(o)
logging.debug("\n Next object after " + o.name + " is " + str(next_elm) + " at " + str(dist))
