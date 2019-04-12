import numpy as np

from model import switch, identifier
from model import loop


_nodes = list()


class Node:

    def __init__(self, switch, loop):
        global _nodes
        _nodes.append(self)

        self.switch = switch
        self.loop = loop
        self.previous_nodes = [None] * 2
        self.next_nodes = [None] * 2
        self.distance_to_next_node = [-1] * 2
        self.id = identifier.generate_node_id

    def add_next_node(self, node):
        self.node.add_previous_node(self)

        if self.next_nodes[0] is None :
            self.next_nodes[0] = node
        else :
            self.next_nodes[1] = node

        self.calculate_distance(node.switch)

    def add_previous_node(self, node):
        if self.previous_nodes[0] is None:
            self.previous_nodes[0] = node
        else:
            self.previous_nodes[1] = node

    def calculate_distance(self, switch):
        distance = -1

        if self.switch.uuid == switch.uuid:
            distance = self.switch.size
        else:
            angle = min(360-abs(switch.angle-self.switch.angle), abs(switch.angle-self.switch.angle))
            distance = switch.loop.size/360 * (angle)

        if self.distance_to_next_node[0] == -1:
            self.distance_to_next_node[0] = distance
        else:
            self.distance_to_next_node[1] = distance


def get_node_id(switch, loop):
    for node in _nodes:
        if node.switch.uuid == switch.uuid and node.loop.uuid == loop.uuid:
            return node.id
    return -1
