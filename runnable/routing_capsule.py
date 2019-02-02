import logging
from settings import network
from model.capsule import Capsule
from model import station

"test de routage d'une capsule"

"""Initialisation"""
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
network.load("../resources/mini_network.json")

"""création d'une capsule à TELECOM Nancy voulant aller à la Gare """
telecom = station.get_by_name("TELECOM Nancy")
stan = station.get_by_name("Stanislas")
capsule = Capsule(station=telecom, destination=stan)


def promenade(c):
    cost = 0
    while 1:
        current = c.current_element
        the_loop = c.loop
        #logging.debug(current)
        if type(current) == station.Station:
            d, n = the_loop.dist_to_next_object(current)
            cost += d
            # print(current.name, d, n)
            if current == c.destination:
                logging.info("capsule " + str(c.id) + " acheminée a bon port, cost = "+str(cost))
                # print("capsule " + str(c.id) + " acheminée a bon port")
                return
            else:
                logging.debug("capsule " + str(c.id) + " passe par station " + current.name)
                c.current_element = n
                d, c.next_element = the_loop.dist_to_next_object(n)
        else: # c'est un switch
            logging.debug("capsule " + str(c.id) + " passe par switch " + str(current.id))
            if the_loop == current.my_loop:  # aiguiller
                c.ask_route(current)
            else : # c'est juste un croisement
                logging.debug("switch in "+ the_loop.name)
                d, c.current_element = the_loop.dist_to_next_object(current)
                d, c.next_element = the_loop.dist_to_next_object(c.current_element)
                cost += d
                logging.debug("next"+ str(c.next_element))
            # print(current.id, d, n)


promenade(capsule)
gare = station.get_by_name("Gare")
capsule.destination = gare
promenade(capsule)
auchan = station.get_by_name("Auchan")
capsule.destination = auchan
promenade(capsule)