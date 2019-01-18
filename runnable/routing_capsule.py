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
gare = station.get_by_name("Gare")
capsule = Capsule(station=telecom, destination=gare)


def promenade(c):
    while 1:
        current = c.current_element
        if type(current) == station.Station:
            the_loop = current.loop
            d, n = the_loop.dist_to_next_object(current)
            # print(current.name, d, n)
            if current == c.destination:
                logging.info("capsule " + str(c.id) + " acheminée a bon port")
                # print("capsule " + str(c.id) + " acheminée a bon port")
                return
            else:
                logging.debug("capsule " + str(c.id) + " passe par station " + current.name)
                c.current_element = n
                d, c.next_element = the_loop.dist_to_next_object(n)
        else: # c'est un switch
            if c.loop == current.my_loop:  # aiguiller
                c.ask_route(current)
            else : # c'est juste un croisement
                d, n = the_loop.dist_to_next_object(current)
                c.current_element = n
                c.next_element = the_loop.dist_to_next_object(n)
            # print(current.id, d, n)




promenade(capsule)