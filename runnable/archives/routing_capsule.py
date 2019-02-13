import logging
from sys import path

from model import station
from model.capsule import Capsule
from settings import network

"test de routage d'une capsule"

"""Initialisation"""
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
network.load("{0}/../resources/{1}".format(path[0], "mini_network.json"))

"""création d'une capsule à TELECOM Nancy voulant aller à la Gare """
telecom = station.get_station_by_name("TELECOM Nancy")
stan = station.get_station_by_name("Stanislas")
capsule = Capsule(departure_station=telecom, destination_station=stan)


def promenade(c):
    cost = 0
    logging.info("capsule n°%d start its trip from %s to %s" % (c.id, c.current_element.name, c.destination.name))
    while 1:
        current = c.current_element
        # logging.debug("capsule n°%d goes through %s" % (c.id, str(current)))
        the_loop = c.loop
        dist, next_e = the_loop.dist_to_next_object(current)
        # logging.debug("si pas routée, next element = " + str(next_e))
        if type(current) == station.Station:
            if current == c.destination:
                logging.info("capsule n°%d arrives at its destination %s with a cost of %d" % (c.id, c.destination, cost))
                return
            else:
                logging.debug("\t capsule n°%d goes through Station %s (cost = %d)" % (c.id, current.name, cost))
                cost += dist
                c.current_element = next_e
                d, c.next_element = the_loop.dist_to_next_object(next_e)
        else:  # c'est un switch
            if the_loop == current.my_loop:  # aiguiller
                logging.debug("\t capsule n°%d be routed by Switch Out %d (cost = %d)" % (c.id, current.id, cost))
                c.ask_route(current)
                if c.loop == the_loop:
                    # je n'ai pas été aiguillée
                    cost += dist
                else:
                    # j'ai été aiguillée
                    d, n = current.other_loop.dist_to_next_object(current)
                    cost += current.size + d
            else:  # c'est juste un croisement
                logging.debug("\t capsule n°%d goes through Switch In n°%d (cost = %d)" % (c.id, current.id, cost))
                cost += dist
                c.current_element = next_e
                d, c.next_element = the_loop.dist_to_next_object(c.current_element)
                # simlog.debug(str(c.current_element))

            # print(current.id, d, n)


promenade(capsule)
gare = station.get_station_by_name("Gare")
capsule.destination = gare
promenade(capsule)
auchan = station.get_station_by_name("Auchan")
capsule.destination = auchan
promenade(capsule)
