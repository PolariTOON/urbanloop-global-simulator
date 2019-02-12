import logging

from model import station
from model import switch
from settings import config
from simulator import sim_loop  # import simulator.sim_loop as sim_loop

_capsules = list()
_capsule_id = 0


class Capsule:
    def __init__(self, departure_station=None, destination_station=None):
        """
        :param departure_station: Initial station of this capsule (Station)
        :param destination_station: The destination station of the capsule (optional - Station)
        """
        global _capsules
        global _capsule_id
        self.id = _capsule_id
        _capsule_id += 1
        _capsules.append(self)

        self.current_element = None
        self.next_element = None
        self.loop = None
        self.destination = destination_station
        self.travelers = list()
        self.trip_event = None
        self.speed = float(config.capsule['max_speed'])
        self.segment_start_tick = 0
        self.segment_ticks_duration = 0

        if departure_station is not None:
            self.current_element = departure_station
            self.next_element = departure_station.next_element
            self.loop = departure_station.loop

    def ask_route(self, current_switch):
        """
        Ask to the selected switch if the capsule should switch or not to another loop to reach its destination.
        :param current_switch: The current switch which decide whether the capsule needs to go on another loop
        """
        change = current_switch.route_capsule_to_station(self.destination)
        if change:
            self._change_loop(current_switch)
        else:
            self._continue()
            logging.info("Capsule n°%d stays on its loop :  %s" %
                         (self.id, self.loop.name))

    def _continue(self):
        """
        The capsule continues its road to the destination, on the same loop
        """
        logging.info("Capsule n°%d arrives at %s from %s" %
                     (self.id, self.next_element.name, self.current_element.name))
        self.current_element = self.next_element

        if type(self.current_element) is switch.Switch and not self.current_element.is_switch_out(self.loop):
            self.next_element = self.current_element.next_element_other
        else:
            self.next_element = self.current_element.next_element

    def _change_loop(self, current_switch):
        """
        The capsule goes to another loop to reach its destination
        :param current_switch: The current switch which has decided to lead the capsule on another loop
        """
        self.current_element = current_switch
        self.next_element = current_switch.next_element_other
        self.loop = current_switch.other_loop
        logging.info("Capsule n°%d is switched to the loop :  %s" %
                     (self.id, self.loop.name))

    def start_trip(self):
        """
        The capsule starts a trip to its destination
        """
        logging.info("Capsule n°%d starts its trip from %s to %s" %
                     (self.id, self.current_element.name, self.destination.name))
        sim_loop.get_env().process(self.update_trip())

    def update_trip(self):
        """
        :return: Trip event generator
        """
        tmp_element = (None, self.current_element)[type(self.current_element) == switch.Switch]
        dist_to_next_element = self.loop.dist_to_next_object(self.current_element, tmp_element)[0]
        time_to_next_element = dist_to_next_element / self.speed
        self.segment_start_tick = sim_loop.get_current_tick()
        self.segment_ticks_duration = 10 * time_to_next_element * sim_loop.get_tick_per_second()
        self.trip_event = sim_loop.get_env().timeout(self.segment_ticks_duration)
        self.trip_event.callbacks.append(lambda event: self.callback_trip_event())
        yield self.trip_event

    def callback_trip_event(self):
        """
        Recursive callback that steps the trip event
        """
        if type(self.next_element) == switch.Switch and self.next_element.is_switch_out(self.loop):
            self.ask_route(self.next_element)
        else:
            self._continue()

        if self.current_element == self.destination:
            logging.info("Capsule n°%d arrives to its destination %s" %
                         (self.id, self.destination.name))
            self.current_element.capsule_queue.put(self)
            self.get_out_traveler()
            return

        sim_loop.get_env().process(self.update_trip())

    def get_in_traveler(self, traveler):
        """
        :param traveler: The traveler who gets in the capsule
        """
        self.destination = station.get_station_by_name(traveler.destination_station_name)
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

    def get_trip_percentage(self):
        """
        :return: The percentage travelled by the capsule on the segment road from the previous to the next element
        """
        if not self.is_aboard() or self.segment_ticks_duration == 0:
            return 0

        return (sim_loop.get_current_tick() - self.segment_start_tick) / self.segment_ticks_duration

    def _get_travelers_id(self):
        """
        Private function used to log information
        :return: String juncture of traveler IDs.
        """
        if len(self.travelers) == 1:
            return self.travelers[0].id
        return " - ".join(map(lambda traveler: traveler.id, self.travelers))

    def show_details(self):
        """
        crée un text contenant toutes les informations à propos de la capsule
        :return: String
        """
        details = "Capsule ID : " + str(self.id)
        details += "\nContains a Travelers : " + str(self.is_aboard())
        details += "\nDestination : " + self.destination.name
        details += "\nCurrent Loop : " + self.loop.name
        details += "\nLast or current element : "
        if type(self.current_element) is station.Station:
            details += "Station " + self.current_element.name
        else:
            details += "Switch " + str(self.current_element.id)
        details += "\nNext element : "
        if type(self.next_element) is station.Station:
            details += "Station " + self.next_element.name
        else:
            details += "Switch " + str(self.next_element.id)
        return details


def reset_simulation():
    global _capsules
    global _capsule_id
    _capsule_id = 0
    for capsule in _capsules:
        del capsule


def get_capsules():
    return _capsules
