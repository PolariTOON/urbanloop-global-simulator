import logging

capsule_id = 0  # type: int


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
            self._continue_on_loop(switch)

    def _change_loop(self, switch):
        """
        Lorsque l'aiguillage indique qu'il faut changer de boucle
            :param switch: l'aiguillage qui a dit qu'il fallait changer de boucle
            :return: void : change "l'élément suivant
        """
        self.current_element = switch.next_element_other
        self.loop = switch.other_loop
        d, self.next_element = self.loop.dist_to_next_object(self.current_element)
        return

    def _continue_on_loop(self, element):
        """
         Lorsque qu'il faut rester sur la boucle (la station n'est pas la destination ou pas accessible ou le switch ne veut pas aiguiller
            :param element: l'element qui fait qu'on doit rester sur la boucle
            :return: void
        """
        self.current_element = element.next_element
        self.next_element = self.loop.dist_to_next_object(self.current_element)
        return

    def get_in_traveler(self, traveler):
        """
        :param traveler: The traveler who gets in the capsule
        """
        self.destination = traveler.destination_station_name
        self.travelers.append(traveler)
        logging.info("[%s] Get traveler (%s) in capsule n°%d" %
                     (traveler.departure_station_name, self._get_travelers_id(), self.id))

    def get_out_traveler(self):
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
