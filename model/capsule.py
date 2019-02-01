import logging

from model.station import get_station_by_name
from model.switch import Switch
from settings import config
from simulator.sim_loop import get_env

capsule_id = 0  # type:int


class Capsule:

    def __init__(self, station=None, destination=None):
        """
        :param station: Initial station of this capsule
        :param destination: The destination station of the capsule (optional)
        """
        global capsule_id
        self.id = capsule_id
        capsule_id += 1
        self.current_element = None
        self.next_element = None
        self.loop = None
        self.destination = destination
        self.travelers = list()
        self.trip_event = None
        self.speed = float(config.capsule['max_speed'])
        self.tick_per_second = (1 / float(config.sim['tick']))
        self.env = get_env()
        if station is not None:
            self.current_element = station
            self.next_element = station.next_element
            self.loop = station.loop

    def ask_route(self, switch):
        """
        Demande au switch de calculer sa route : va déclencher le changement ou non de boucle
        :param  switch : Switch "suivant" a qui la capsule demande d'etre routé (Switch) OBLIGATOIRE
        :return: void : mise à jour
        """
        change = switch.route_capsule_to_station(self.destination)
        if change:
            self._change_loop(switch)
        else:
            self._continue()
            logging.info("Capsule n°%d stays on its loop :  %s" %
                         (self.id, self.loop.name))

    def _continue(self):
        logging.info("Capsule n°%d arrives at %s from %s" %
                     (self.id, self.next_element.name, self.current_element.name))
        self.current_element = self.next_element
        self.next_element = self.current_element.next_element

    def _change_loop(self, switch):
        self.current_element = self.next_element
        self.next_element = switch.next_element_other
        self.loop = switch.other_loop
        logging.info("Capsule n°%d is switched to the loop :  %s" %
                     (self.id, self.loop.name))

    def start_trip(self):
        logging.info("Capsule n°%d starts its trip from %s to %s" %
                     (self.id, self.current_element.name, self.destination.name))
        self.env.process(self.update_trip())

    def update_trip(self):
        """
        :return: Trip event generator
        """
        time_to_next_element = self.loop.dist_to_next_object(self.current_element)[0] / self.speed
        self.trip_event = self.env.timeout(time_to_next_element * self.tick_per_second)
        self.trip_event.callbacks.append(lambda event: self.callback_trip_event())
        yield self.trip_event

    def callback_trip_event(self):
        """
        Recursive callback that steps the trip event
        """
        if type(self.next_element) == Switch:
            self.ask_route(self.next_element)
        else:
            self._continue()

        if self.current_element == self.destination:
            logging.info("Capsule n°%d arrives to its destination %s" %
                         (self.id, self.destination.name))
            return

        self.env.process(self.update_trip())

    def get_in_traveler(self, traveler):
        """
        :param traveler: The traveler who gets in the capsule
        """
        self.destination = get_station_by_name(traveler.destination_station_name)
        self.travelers.append(traveler)
        logging.info("[%s] Get traveler (%s) in capsule n°%d" %
                     (traveler.departure_station_name, self._get_travelers_id(), self.id))

    def get_out_traveler(self):
        """
        Clear the traveler list and set the destination to None.
        """
        logging.info("[%s] Get traveler (%s) out of capsule n°%d" %
                     (self.destination.name, self._get_travelers_id(), self.id))
        self.destination = None
        self.travelers.clear()

    def is_aboard(self):
        """
        :return: True if someone is aboard the capsule. Otherwise returns False
        """
        return len(self.travelers) > 0

    def _get_travelers_id(self):
        """
        Private function used to log information
        :return: String juncture of traveler IDs.
        """
        if len(self.travelers) == 1:
            return self.travelers[0].id
        return " - ".join(map(lambda traveler: traveler.id, self.travelers))
