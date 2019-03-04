import logging

import model.loop as ML
from model.switch import Switch
from settings import network

"""fichier de test d'import d'un réseau """

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
# logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

network_path = '../resources/mini_network.json'
try:
    with open(network_path, "r") as file:
        None  # TODO WTF ?
except FileNotFoundError:
    network_path = 'resources/mini_network.json'

network.load(network_path)

# on charge toutes les boucles créées
for name, l in ML.all_loops.items():
    logging.info("\t %s: circumference %d ; coordinates of the center : x = %d, y=%d ;" % (l.name, l.size, l.x, l.y))
    logging.debug("\t Stations : " + str([[st.name, st.id] for st in l.stations]))
    logging.debug("\t  -- an object in the station = [[nature, objectId, angle in the station]] -- ")
    # objects est un attributs des loops qui contient la succession des éléments
    logging.debug("\t" + str([[o[0], o[1].id, o[2]] for o in l.objects]))
    for sw in l.switches:
        if sw.my_loop == l:
            logging.info("\t \t Table of the switch n°%d: %s" %(sw.id, str(sw.table)))
    # simlog.debug(l.lengths)

'''loop_nancy = model_loop.get_by_name("Nancy")
o = loop_nancy.objects[2][1]
dist, next_elm = loop_nancy.dist_to_next_object(o)
simlog.debug("\n Next object after " + o + " is " + str(next_elm) + " at " + str(dist))
'''

loop_laxou = ML.get_by_name("Laxou")
for obj in loop_laxou.objects:
    # print(o);
    o = obj[1]
    dist, next_elm = loop_laxou.dist_to_next_object(o);
    if type(next_elm) is Switch:
        logging.debug("\n Next object after %s is Switch n°%d at %d" % (str(obj), next_elm.id, dist))
    else:
        logging.debug("\n Next object after %s is Station %s at %d" % (str(obj), next_elm.name, dist))
