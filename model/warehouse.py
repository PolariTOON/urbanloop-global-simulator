from model import identifier
from model import queue
from model import switch
from model import controller
from settings import simlog

_warehouses = list()
_controller = None


class Warehouse:
    def __init__(self, loop, angle, capacity=float('inf'), next_element=None):
        global _warehouses
        _warehouses.append(self)
        global _controller
        _controller = controller.get_controller()

        self.uuid = identifier.generate_unique()
        self.id = identifier.generate_warehouse_id()
        self.angle = angle
        self.capacity = capacity
        self.loop = loop
        self.next_element = next_element
        self.capsule_queue = queue.Queue(maxsize=self.capacity)
        self.name = "warehouse_%s" % self.loop.name
        self.section_loop = None

    def reset_simulation(self):
        self.capsule_queue = queue.Queue(maxsize=self.capacity)

    def send_capsule(self, station_destination, priority):
        simlog.info("an empty capsule left warehouse %d to %s" % (self.id, station_destination.name))
        if self.capsule_queue.qsize() > 0:
            capsule_to_send = self.capsule_queue.get()
            capsule_to_send.destination = station_destination
            if True:  # TODO eviter de sortir alors que y'a déjà une capsule sur la sortie
                capsule_to_send.start_trip()

    def capsule_passing(self, capsule):
        _controller.update_from_switch(capsule)

    def end_capsule_trip(self, capsule):
        _controller.stop_timer(capsule)

def which_warehouse_before(station_destination):
    """
    trouver le warehouse dont la capsule doit partir pour arriver à la station au plus vite
    :param station_destination:
    :return: l'entrepôt le plus proche "en amont"
    """
    go_from = None
    cost_go_from = float('inf')
    for cand_warehouse in _warehouses:
        if cand_warehouse.capsule_queue.qsize() > 0:
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
        if cand_warehouse.capsule_queue.qsize() < cand_warehouse.capacity:
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
