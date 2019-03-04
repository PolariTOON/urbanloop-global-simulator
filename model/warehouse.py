from settings import simlog
from model import queue
from model import switch
from model import station

_warehouses = list()
_warehouse_id = -1


class Warehouse:
    def __init__(self, loop, angle, capacity=float('inf'), next_element=None):
        global _warehouses
        global _warehouse_id
        self.id = _warehouse_id
        _warehouse_id += 1
        _warehouses.append(self)
        self.angle = angle
        self.capacity = capacity
        self.loop = loop
        self.next_element = next_element
        self.capsule_queue = queue.Queue(maxsize=self.capacity)
        self.name = "warehouse_%s" % self.loop.name

    def show_details(self):
        """
        crée un text contenant toutes les informations à propos de l'entrepôt
        :return: String
        """
        details = "Warehouse objectId : " + str(self.id)
        details += "\nLoop : " + self.loop.name
        details += "\nCapacity : " + str(self.capacity)
        details += "\nNext element : "
        if type(self.next_element) is station.Station:
            details += "Station " + self.next_element.name
        else:
            details += "Switch " + str(self.next_element.id)
        details += "\nCapsules (%d): " % self.capsule_queue.qsize()
        #if self.capsule_queue.qsize() != 0:
            # l = self.capsule_queue.list()
            # for c in l:
            #    details += "\n    Capsule #{0}".format(c.id)
        return details

    def send_capsule(self, station):
        simlog.info("an empty capsule left warehouse %d to %s" % (self.id, station.name))
        capsule = self.capsule_queue.get()
        capsule.destination = station
        if True:  # TODO eviter de sortir alors que y'a déjà une cpasule sur la sortie
            capsule.start_trip()


def which_warehouse_before(station):
    """
    trouver le warehouse dont la capsule doit partir pour arriver à la station au plus vite
    :param station:
    :return: l'entrepôt le plus proche "en amont"
    """
    go_from = None
    cost_go_from = float('inf')
    for candidat in _warehouses:
        if candidat.capsule_queue.qsize() > 0:
            if candidat.loop is station.loop:
                return candidat
            cost = switch.cost_between(candidat, station)
            if cost < cost_go_from:
                go_from = candidat
                cost_go_from = cost
    return go_from


def which_warehouse_after(station):
    """
    trouver le warehouse vers lequel la capsule doit partir depuis la station
    :param station:
    :return: l'entrepôt le plus proche "en aval"
    """
    go_to = None
    cost_go_to = float('inf')
    for candidat in _warehouses:
        if candidat.capsule_queue.qsize() < candidat.capacity:
            if candidat.loop is station.loop:
                return candidat
            cost = switch.cost_between(station, candidat)
            if cost < cost_go_to:
                go_to = candidat
                cost_go_to = cost
    return go_to


def get_warehouses():
    return _warehouses