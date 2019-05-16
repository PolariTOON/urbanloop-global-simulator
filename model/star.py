import math

from model import identifier
from model import station
from model import switch
from model import warehouse
from settings import config
from settings import simlog
from simulator import converter
from simulator import sim_loop

_stars = list()


class Star:
    def __init__(self, departure, destination):
        """
        :param departure_station: Initial station of this capsule (Station)
        :param destination_station: The destination station of the capsule (optional - Station)
        """
        global _stars
        _stars.append(self)

        self.uuid = identifier.generate_unique()
        self.id = identifier.generate_capsule_id()
        self.departure = switch.get_switch_by_node(departure)
        self.loop = departure.loop
        self.destination = switch.get_switch_by_node(destination)
        self.segment_length = 0

    def get_segment_angle(self):
        """
        :return: The segmentPercentage
        """
        return (0.5)

def get_stars():
    """
    :return: All capsules of the network
    """
    return _stars
