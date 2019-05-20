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
    def __init__(self, node1, node2):
        """
        :param node1: Start of the section
        :param node: End of the section
        """
        global _stars
        _stars.append(self)

        self.uuid = identifier.generate_unique()
        self.id = identifier.generate_star_id()
        self.switch1 = switch.get_switch_by_node(node1)
        self.loop1 = node1.loop
        self.switch2 = switch.get_switch_by_node(node2)
        self.loop2 = node2.loop
        self.segment_length = 0

    def get_pos(self):
        """
        :return: The position where the image must be dispayed
        """

        x_in, y_in, x_out, y_out = get_switch_positions(capsule.current_element)
        radius_angle_loop_in = math.radians(node1.loop)
        radius_angle_loop_out = math.radians(node2.loop)
        loop_in_radius = math.floor(node1.loop.size / (2 * math.pi))
        loop_out_radius = math.floor(node2.size / (2 * math.pi))
        x_in = node1.loop.x + math.cos(radius_angle_loop_in) * loop_in_radius
        y_in = node1.loop.y + math.sin(radius_angle_loop_in) * loop_in_radius
        x_out = node2.loop.x + math.cos(radius_angle_loop_out) * loop_out_radius
        y_out = node2.loop.y + math.sin(radius_angle_loop_out) * loop_out_radius

        return (x_in * (1 - 0.5) + x_out * 0.5, y_in * (1 - 0.5) + y_out * 0.5)

def get_list_pos():
    l=list()
    for i in get_stars():
        l.append(i.get_pos())
    return(l)



def get_stars():
    """
    :return: All capsules of the network
    """
    return _stars
