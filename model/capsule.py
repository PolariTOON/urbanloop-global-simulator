import math

from model import identifier
from model import station
from model import switch
from model import controller
from model import warehouse
from settings import config
from settings import simlog
from simulator import converter
from simulator import sim_loop

_capsules = []
_empty_capsules = []


class Capsule:
    def __init__(self, departure_station, destination_station=None):
        """
        :param departure_station: Initial station of this capsule (Station)
        :param destination_station: The destination station of the capsule (optional - Station)
        """
        global _capsules
        _capsules.append(self)
        global _empty_capsules
        _empty_capsules.append(self)

        self.segment_real_tick = 0
        self.stopped = False
        self.uuid = identifier.generate_unique()
        self.id = identifier.generate_capsule_id()
        self.current_element = None
        self.next_element = None
        self.loop = None
        self.destination = destination_station
        self.travelers = []
        self.trip_event = None
        self.descent_event = None
        self.speed = float(config.capsule['max_speed'])
        self.segment_length = 0
        self.segment_start_tick = 0
        self.segment_ticks_duration = 0
        self.moving = False
        self.priority = 10

        if departure_station is not None:
            self.current_element = departure_station
            self.next_element = departure_station.next_element
            self.loop = departure_station.loop

    def ask_route(self, current_switch):
        """
        Ask to the selectedObject switch if the capsule should switch or not to another station to reach its destination.
        :param current_switch: The current switch which decide whether the capsule needs to go on another station
        """

        change = current_switch.route_capsule_to_station(self)
        if change:
            self._change_loop(current_switch)
        else:
            self._continue()
            simlog.info("Capsule %d stays on its loop" % self.id, self.loop)

    def _continue(self):
        """
        The capsule continues its road to the destination, on the same station
        """
        simlog.debug("Capsule %d continues its trip to %s" % (self.id, self.destination.name),
                     self.current_element.name, self.next_element.name)
        self.current_element = self.next_element

        if type(self.current_element) is switch.Switch and not self.current_element.is_switch_out(self.loop):
            self.next_element = self.current_element.next_element_other
        else:
            self.next_element = self.current_element.next_element

    def _change_loop(self, current_switch):
        """
        The capsule goes to another station to reach its destination
        :param current_switch: The current switch which has decided to lead the capsule on another station
        """
        self.current_element = current_switch
        self.next_element = current_switch
        sim_loop.recorder.add_exiting_loop(self.loop)
        self.loop = current_switch.other_loop
        sim_loop.recorder.add_joining_loop(self.loop)
        simlog.info("Capsule %d is switched (destination %s)" % (self.id, self.destination.name),
                    current_switch.my_loop, self.loop)

    def start_trip(self):
        """
        The capsule starts a trip to its destination
        """
        controller.get_controller().temps_moy_stat(self.id, sim_loop.get_simulated_time())
        simlog.info(
            "Capsule %d (%s) starts its trip to %s" % (self.id, self._get_capacity_state(), self.destination.name),
            self.current_element)
        sim_loop.recorder.add_traveling_distance(switch.cost_between(self.current_element, self.destination), self)
        sim_loop.recorder.add_departure_from_station(self.current_element)
        simlog.debug("Amount of capsules : %d" % self.current_element.capsule_queue.qsize(), self.current_element)
        for a_traveler in self.travelers:
            a_traveler.trip_start_tick = sim_loop.get_current_tick()
        if self.travelers:
            _empty_capsules.remove(self)
        self.moving = True
        sim_loop.get_env().process(self.update_trip())

    def update_trip(self):
        """
        :return: Trip event generator
        """
        dist_to_next_element = self.loop.distance_between(self.current_element, self.next_element)
        self.segment_length = dist_to_next_element
        time_to_next_element = dist_to_next_element / self.speed
        self.segment_start_tick = sim_loop.get_current_tick()
        self.segment_ticks_duration = time_to_next_element * sim_loop.get_tick_per_second()
        self.segment_real_tick = self.segment_start_tick
        self.trip_event = sim_loop.get_env().timeout(self.segment_ticks_duration)

        self.trip_event.callbacks.append(lambda event: self.callback_trip_event())
        yield self.trip_event

    def callback_trip_event(self):
        """
        Recursive callback that steps the trip event.
        This function is called when the capsule arrives to the next_element which isn't
        updated yet as the current_element.
        """
        """
        Cette partie en commentaire correspond à des tests effectué pour arreté une capsule si lorsqu'elle
        arrive à un noeud elle peut continuer sa route. Typiquement si il n'y a pas une autre capsule qui arrive
        (90% du trajet) ou qui vient juste d'en partir (10% du trajet).
        Cette méthode s'est soldé par un échec.

        test = True
        for i in get_capsules():
            print("nextid",i.next_element.id)
            print("selfid",self.next_element.id)
            if (i.next_element == self.next_element):
                print("n",i.get_segment_trip_percentage())
            if i.get_segment_trip_percentage() >= 90 and i.next_element == self.next_element:
                test=False
            if (i.current_element == self.next_element):
                print("c",i.get_segment_trip_percentage())
            if i.get_segment_trip_percentage() <= 10 and i.current_element == self.next_element:
                test=False
        if test:
        self.speed=float(config.capsule['max_speed'])"""
        if type(self.next_element) == switch.Switch and self.next_element.is_switch_out(self.loop):
            self.ask_route(self.next_element)
        else:
            self.next_element.capsule_passing(self)
            self._continue()
        # optimisation : si une capsule vide en direction d'un entrepot passe devant une station vide elle se déroute
        if not (self.is_aboard()) and type(self.next_element) is station.Station and type(
                self.destination) is warehouse.Warehouse:
            # simlog.debug("Rerouted ? capsule %d direction %s, station qsize %d, estimated_count %d, capacity %d" % (self.id, self.destination.name, self.next_element.capsule_queue.qsize(), self.next_element.estimated_capsules_number(), self.next_element.capacity), self.next_element.name)
            if self.next_element.capsule_queue.qsize() <= 1 and (
                    self.next_element.estimated_capsules_number() < self.next_element.capacity - 1 or self.next_element.traveler_queue.qsize() >= 1):
                simlog.debug("The capsule %d direction %s is rerouted to %s (%d/%d)" % (
                    self.id, self.destination.name, self.next_element.name,
                    self.next_element.estimated_capsules_number(),
                    self.next_element.capacity), self.current_element, self.next_element)
                self.destination = self.next_element
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
        controller.get_controller().temps_moy_stat(self.id, sim_loop.get_simulated_time())
        self.current_element.end_capsule_trip(self)
        simlog.info("Capsule %d (%s) ends its trip" %
                    (self.id, self._get_capacity_state()), self.destination.name)
        sim_loop.recorder.add_arrival_to_station(self.current_element)
        self.current_element.capsule_queue.put(self)
        self.destination = None
        simlog.debug(
            "Contains %d capsules now" % (self.current_element.capsule_queue.qsize()), self.current_element.name)
        self.moving = False
        if self.travelers:
            _empty_capsules.append(self)
            simlog.debug("Start descent in capsule %d" % self.id, self.destination)
            traveler = self.travelers[0]
            traveler.stats()
            trip_time = sim_loop.get_simulated_time() - sim_loop.get_simulated_time(traveler.trip_start_tick)
            sim_loop.recorder.add_traveling_time_traveler(trip_time, traveler)
            self.descent_event = sim_loop.get_env().timeout(converter.random_ascent_descent_duration())
            self.descent_event.callbacks.append(lambda event: self.get_out_traveler())
            yield self.descent_event

    def get_in_traveler(self, traveler):
        """
        :param traveler: The traveler who gets in the capsule
        """
        self.destination = traveler.destination_station
        self.travelers.append(traveler)
        simlog.info("Traveler %s gets in capsule %d" % (self._get_travelers_id(), self.id), traveler.departure_station,
                    self.destination)

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

    def get_segment_traveled_angle(self):
        """
        :return: The segmentPercentage travelled by the capsule on the segment road from the previous to the next element
        """
        if self.destination is None or self.segment_ticks_duration == 0:
            return 0

        return (sim_loop.get_current_tick() - self.segment_real_tick) * self.get_angle_per_tick()

    def get_segment_traveled_distance(self):
        """
        :return: The segmentPercentage travelled by the capsule on the segment road from the previous to the next element
        """
        if self.destination is None or self.segment_ticks_duration == 0:
            return 0

        return (sim_loop.get_current_tick() - self.segment_real_tick) * self.get_meter_per_tick()

    def get_segment_trip_percentage(self):
        """
        :return: The segmentPercentage travelled by the capsule on the segment road from the previous to the next element
        """
        if self.destination is None or self.segment_ticks_duration == 0:
            return 0

        return ((sim_loop.get_current_tick() - self.segment_real_tick) / self.segment_ticks_duration) * 100

    def get_meter_per_tick(self):
        """
        :return: The distance traveled each tick by a capsule at the defined speed
        """
        return float(self.speed / sim_loop.get_tick_per_second())

    def get_angle_per_tick(self):
        """
        :return: The distance traveled each tick by a capsule at the defined speed
        """
        return self.get_meter_per_tick() / (self.loop.size / (2 * math.pi))

    def get_station_queue_index(self):
        if type(self.current_element) is station.Station:
            return self.current_element.capsule_queue.index_of(self)
        return -1

    def _get_travelers_id(self):
        """
        Private function used to log information
        :return: String juncture of traveler IDs.
        """
        if len(self.travelers) == 1:
            return self.travelers[0].id
        # TODO DEBUG return " - ".join(map(lambda traveler: traveler.objectId, self.travelers))
        return self.travelers[0].id

    def _get_capacity_state(self):
        """
        Private function used to log information
        :return: The string state of the capsule traveler_list
        """
        number = len(self.travelers)
        return ((str(number) + ' traveler', str(number) + ' travelers')[number > 1], 'Empty')[number == 0]

    def get_position(self):
        """
        :return: (x, y)
        """
        if self.current_element is self.next_element:
            # In this case, current_element and next_element can only be switches
            t = self.get_segment_traveled_distance() / self.current_element.size
            x_in, y_in, x_out, y_out = self.current_element.get_positions()
            return x_in * (1 - t) + x_out * t, y_in * (1 - t) + y_out * t
        else:
            # In this case, current_element and next_element can be station or switch
            angle = self.current_element.get_angle(self.loop)
            trip_angle = self.get_segment_traveled_angle()
            if self.loop.clockwise:
                radius_angle = math.radians(angle) - trip_angle
            else:
                radius_angle = math.radians(angle) + trip_angle
            loop_radius = self.loop.get_radius()
            return self.loop.x + math.cos(radius_angle) * loop_radius, self.loop.y + math.sin(radius_angle) * loop_radius

    def serialize(self):
        x, y = self.get_position()
        return {
            'jsonType': 'capsule',
            'uuid': str(self.uuid),
            'id': self.id,
            'x': x,
            'y': y,
            'travelerNumber': len(self.travelers),
            'destination': self.destination.name if self.destination is not None else "None",
            'moving': self.moving,
            'outerCircle': self.loop.name,
            'current_element': self.current_element.name,
            'next_element': self.next_element.name,
            'currentElementUuid': str(self.current_element.uuid),
            'stationIndex': self.get_station_queue_index()
        }


def get_incoming_capsule(destination):
    return [capsule for capsule in _capsules if capsule.destination is destination]


def get_capsules():
    """
    :return: All capsules of the network
    """
    return _capsules


def get_empty_capsules():
    """
    :return: All the empty capsules of the network
    """
    return _empty_capsules


def reset_simulation():
    """
    This function will reset every capsules of the network
    """
    global _capsules
    for capsule in _capsules:
        del capsule
    _capsules = []
