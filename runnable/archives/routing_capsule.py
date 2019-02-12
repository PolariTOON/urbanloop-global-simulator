import logging
from settings import network
from model.capsule import Capsule
from model import station
from sys import path

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
    logging.info("capsule " + str(c.id)
                 + " part de la station " + c.current_element.name + " vers la station " + c.destination.name)
    while 1:
        current = c.current_element
        # logging.debug("capsule " + str(c.id) + " passe par" + str(current))
        the_loop = c.loop
        dist, next_e = the_loop.dist_to_next_object(current)
        # logging.debug("si pas routée, next element = " + str(next_e))
        if type(current) == station.Station:
            if current == c.destination:
                logging.info("capsule " + str(c.id) + " acheminée a bon port, cost = " + str(cost))
                return
            else:
                logging.debug("capsule " + str(c.id) + " passe par station " + current.name + ", cout = " + str(cost))
                cost += dist
                c.current_element = next_e
                d, c.next_element = the_loop.dist_to_next_object(next_e)
        else:  # c'est un switch
            if the_loop == current.my_loop:  # aiguiller
                logging.debug(
                    "capsule " + str(c.id) + " passe par switch out " + str(current.id) + ", cout = " + str(cost))
                c.ask_route(current)
                if c.loop == the_loop:
                    # je n'ai pas été aiguillée
                    cost += dist
                else:
                    # j'ai été aiguillée
                    d, n = current.other_loop.dist_to_next_object(current)
                    cost += current.size + d
            else:  # c'est juste un croisement
                logging.debug(
                    "capsule " + str(c.id) + " passe par switch in " + str(current.id) + ", cout = " + str(cost))
                cost += dist
                c.current_element = next_e
                d, c.next_element = the_loop.dist_to_next_object(c.current_element)
                # logging.debug(str(c.current_element))

            # print(current.id, d, n)


promenade(capsule)
gare = station.get_station_by_name("Gare")
capsule.destination = gare
promenade(capsule)
auchan = station.get_station_by_name("Auchan")
capsule.destination = auchan
promenade(capsule)
