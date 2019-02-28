from model import station
from model import switch
from settings import config
from settings import simlog
from simulator import converter
from simulator import sim_loop

_capsules = list()
_capsule_id = 0


class Capsule:
    def __init__(self, departure_station, destination_station=None):
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
        self.descent_event = None
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
            simlog.info("Capsule %d stays on its loop" % self.id, self.loop)

    def _continue(self):
        """
        The capsule continues its road to the destination, on the same loop
        """
        simlog.debug("Capsule %d continues its trip" % self.id, self.next_element.name, self.current_element.name)
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
        simlog.info("Capsule %d is switched" % self.id, current_switch.my_loop, self.loop)

    def start_trip(self):
        """
        The capsule starts a trip to its destination
        """
        simlog.info("Capsule %d (%s) starts its trip" % (self.id, self._get_capacity_state()),
                    self.current_element, self.destination)
        simlog.debug("Amount of capsules : %d" % self.current_element.capsule_queue.qsize(), self.current_element)
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
        Recursive callback that steps the trip event.
        This function is called when the capsule arrives to the next_element which isn't
        updated yet as the current_element.
        """
        if type(self.next_element) == switch.Switch and self.next_element.is_switch_out(self.loop):
            self.ask_route(self.next_element)
        else:
            self._continue()

        if self.current_element == self.destination:
            if self.current_element.capsule_queue.full():
                simlog.info("Capsule %d (%s) arrives to its destination but the station is full !" %
                            (self.id, self._get_capacity_state()), self.destination.name)
                simlog.debug("%s contains %d capsules now" % (
                    self.current_element.name, self.current_element.capsule_queue.qsize()))
                self.current_element.drain()
            else:
                sim_loop.get_env().process(self.end_trip())
                return

        sim_loop.get_env().process(self.update_trip())

    def end_trip(self):
        simlog.info("Capsule %d (%s) ends its trip" %
                    (self.id, self._get_capacity_state()), self.destination.name)
        self.current_element.capsule_queue.put_nowait(self)
        self.destination = None
        simlog.debug(
            "%s contains %d capsules now" % (self.current_element.name, self.current_element.capsule_queue.qsize()))
        if self.travelers:
            simlog.debug("Start descent in capsule %d" % self.id, self.destination)
            self.descent_event = sim_loop.get_env().timeout(converter.random_ascent_descent_duration())
            self.descent_event.callbacks.append(lambda event: self.get_out_traveler())
            yield self.descent_event

    def get_in_traveler(self, traveler):
        """
        :param traveler: The traveler who gets in the capsule
        """
        self.destination = traveler.destination_station
        self.travelers.append(traveler)
        simlog.info("Traveler %s gets in capsule %d" % (self._get_travelers_id(), self.id), traveler.departure_station)

    def get_out_traveler(self):
        """
        Clear the traveler list and set the destination to None.
        """
        simlog.info("Traveler %s gets out capsule %d" % (self._get_travelers_id(), self.id), self.destination)
        self.travelers.clear()

    def is_aboard(self):
        """
        :return: True if someone is aboard the capsule. Otherwise returns False
        """
        return len(self.travelers) > 0

    def get_segment_trip_percentage(self):
        """
        :return: The segmentPercentage travelled by the capsule on the segment road from the previous to the next element
        """
        if not self.is_aboard() or self.destination is None or self.segment_ticks_duration == 0:
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

    def _get_capacity_state(self):
        """
        Private function used to log information
        :return: The string state of the capsule traveler_list
        """
        number = len(self.travelers)
        return ((str(number) + ' traveler', str(number) + ' travelers')[number > 1], 'Empty')[number == 0]

    def show_details(self):
        """
        crée un text contenant toutes les informations à propos de la capsule
        :return: String
        """
        details = "Capsule ID : " + str(self.id)
        details += "\nContains a Travelers : " + str(self.is_aboard())
        if self.destination is not None:
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


def get_incoming_capsule(destination):
    return [capsule for capsule in _capsules if capsule.destination is destination]


def get_capsules():
    """
    :return: All capsules of the network
    """
    return _capsules


def reset_simulation():
    """
    This function will reset every capsules of the network
    """
    global _capsules
    global _capsule_id
    _capsule_id = 0
    for capsule in _capsules:
        del capsule
