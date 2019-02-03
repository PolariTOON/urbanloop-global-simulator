import logging

from simulator import sim_loop # import simulator.sim_loop as sim_loop
from model.station import get_station_by_name
from model.switch import Switch
from settings import config

_capsules = list()
_capsule_id = 0


class Capsule:
    def __init__(self, station=None, destination=None):
        """
        :param  station: Initial station of this capsule (Station)
        :param destination: The destination station of the capsule (optional - Station)
        """
        global _capsules
        global _capsule_id
        self.id = _capsule_id
        _capsule_id += 1
        _capsules.append(self)

        self.current_element = None
        self.next_element = None
        self.loop = None
        self.destination = destination
        self.travelers = list()
        self.trip_event = None
        self.speed = float(config.capsule['max_speed'])
        self.segment_start_tick = 0
        self.segment_ticks_duration = 0

        if station is not None:
            self.current_element = station
            self.next_element = station.next_element
            self.loop = station.loop

    def ask_route(self, switch):
        """
        Ask to the selected switch if the capsule should switch or not to another loop to reach its destination.
        :param switch: The current switch which decide whether the capsule needs to go on another loop
        """
        change = switch.route_capsule_to_station(self.destination)
        if change:
            self._change_loop(switch)
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
        self.next_element = self.current_element.next_element

    def _change_loop(self, switch):
        """
        The capsule goes to another loop to reach its destination
        :param switch: The current switch which has decided to lead the capsule on another loop
        """
        self.current_element = switch
        self.next_element = switch.next_element_other
        self.loop = switch.other_loop
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
        time_to_next_element = self.loop.dist_to_next_object(self.current_element)[0] / self.speed
        self.segment_start_tick = sim_loop.get_current_tick()
        self.segment_ticks_duration = time_to_next_element * sim_loop.get_tick_per_second()
        self.trip_event = sim_loop.get_env().timeout(self.segment_ticks_duration)
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
            self.get_out_traveler()
            return

        sim_loop.get_env().process(self.update_trip())

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

    def get_trip_percentage(self):
        """
        :return: The percentage travelled by the capsule on the segment road from the previous to the next element
        """
        if not self.is_aboard():
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


def reset_simulation():
    global _capsules
    global _capsule_id
    _capsule_id = 0
    for capsule in _capsules:
        del capsule
