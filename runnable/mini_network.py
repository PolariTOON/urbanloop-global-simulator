import logging

import model.loop as ML
from settings import network


"""fichier de test d'import d'un réseau """


network.load('../resources/mini_network.json')

# on charge toutes les boucles créées
for name, l in ML.all_loops.items():
    logging.info("\n" + l.name + ", circonférence : "+ l.size + "coordonnées du centre = " + l.x + l.y)
    logging.debug("\t Stations : " + [[st.name, st.id] for st in l.stations])
    logging.debug("\t  -- an object in the loop = [[nature, id, angle in the loop]] -- ")
    logging.debug("\t" + [[o[0], o[1].id, o[2]] for o in l.objects])  # objects est un attributs des loops qui contient la succession des éléments
    for sw in l.switches:
        if sw.my_loop == l:
            logging.info("\t \t table of switch " + sw.id + " : " + sw.table)
    # logging.debug(l.lengths)

loop_nancy = ML.get_by_name("Nancy")
o = loop_nancy.objects[2][1]
dist, next_elm = loop_nancy.dist_to_next_object(o)
logging.debug("\n Next object after " + o.name + " is " + next_elm + " at " + dist)
