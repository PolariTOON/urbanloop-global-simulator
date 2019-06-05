from model import identifier
from model import queue
from model import switch
from model import station
from model import controller
from model import capsule
from settings import simlog

_warehouses = list()


class Warehouse:
    def __init__(self, loop, angle, capacity=float('inf'), next_element=None):
        global _warehouses
        _warehouses.append(self)
        self.capsules = capsule.get_capsules()
        self.uuid = identifier.generate_unique()
        self.id = identifier.generate_warehouse_id()
        self.angle = angle
        self.capacity = capacity
        self.loop = loop
        self.next_element = next_element
        self.capsule_queue = queue.Queue(maxsize=self.capacity)
        self.name = "warehouse_%s" % self.loop.name
        self.section_loop = None
        self.nb_to_send = 0

    def reset_simulation(self):
        self.capsule_queue = queue.Queue(maxsize=self.capacity)

    def drain(self, station_destination=None, priority=-1):

        if self.capsule_queue.qsize() > 0:
            capsule_to_send = self.capsule_queue.get()
            if station_destination is None:
                station_destination = station.get_almost_empty_station(self)
            capsule_to_send.destination = station_destination
            if priority >= 0:
                capsule_to_send.priority = priority
            test = True
            for i in self.capsules:
                if i.get_segment_trip_percentage() >= 90 and i.next_element == self:
                    test = False
                if i.get_segment_trip_percentage() <= 10 and i.current_element == self:
                    test = False
            if test:
                simlog.info("an empty capsule left warehouse %d to %s with priority %d" % (self.id, station_destination.name, priority))
                capsule_to_send.start_trip()
            else:
                self.capsule_queue.put(capsule_to_send)

    def capsule_passing(self, capsule):
        controller.get_controller().update_from_switch(capsule)

    def end_capsule_trip(self, capsule):
        controller.get_controller().stop_timer(capsule)


def which_warehouse_before(station_destination):
    """
    trouver le warehouse dont la capsule doit partir pour arriver à la station au plus vite
    :param station_destination:
    :return: l'entrepôt le plus proche "en amont"
    """
    go_from = None
    cost_go_from = float('inf')
    for cand_warehouse in _warehouses:
        if cand_warehouse.loop is station_destination.loop:
            return cand_warehouse
        cost = switch.cost_between(cand_warehouse, station_destination)
        if cost < cost_go_from:
            go_from = cand_warehouse
            cost_go_from = cost
    return go_from


def which_warehouse_after(station_source):
    """
    trouver le warehouse vers lequel la capsule doit partir depuis la station
    :param station_source:
    :return: l'entrepôt le plus proche "en aval"
    """
    go_to = None
    cost_go_to = float('inf')
    for cand_warehouse in _warehouses:
        # if cand_warehouse.capsule_queue.qsize() < cand_warehouse.capacity:
        if cand_warehouse.loop is station_source.loop:
            return cand_warehouse
        cost = switch.cost_between(station_source, cand_warehouse)
        if cost < cost_go_to:
            go_to = cand_warehouse
            cost_go_to = cost
    return go_to


def get_warehouses():
    return _warehouses


def reset_simulation():
    """
    This function will reset every warehouses of the network
    """
    for warehouse in _warehouses:
        warehouse.reset_simulation()
