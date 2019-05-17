import numpy as np

from model import switch, identifier
from model import loop
from model import identifier


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
        self.id = identifier.generate_node_id()

    def add_next_node(self, node):
        node.add_previous_node(self)

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

    def remove_next(self, node):
        if self.next_nodes[0].id == node.id:
            node.remove_previous(self)
            self.next_nodes[0] = self.next_nodes[1]
            self.next_nodes[1] = None
        elif self.next_nodes[1].id == node.id:
            node.remove_previous(self)
            self.next_nodes[1] = None

    def remove_previous(self, node):
        if self.previous_nodes[0].id == node.id:
            self.previous_nodes[0] = self.previous_nodes[1]
            self.previous_nodes[1] = None
        else:
            self.previous_nodes[1] = None

    def calculate_distance(self, a_switch):
        """
        Calcule la longueur du troncon entre lui même et le switch/warehouse/station entré en paramètre
        :param switch: switch/warehouse/station d'arrivée du troncon dont on calcule la longeur
        :return: met jour l'attribut distance_to_next_node
        """
        distance = -1

        if self.switch.uuid == a_switch.uuid:
            distance = self.switch.size
        elif type(self.switch) is switch.Switch:
            if self.switch.loop.uuid == self.loop.uuid:
                angle2 = self.switch.angle_my_loop
            else:
                angle2 = self.switch.angle_other_loop

            if type(a_switch) is switch.Switch:
                if a_switch.loop.uuid == self.loop.uuid:
                    angle1 = a_switch.angle_my_loop
                else:
                    angle1 = a_switch.angle_other_loop
            else:
                angle1 = a_switch.angle

            angle = min(360-abs(angle1-angle2), abs(angle1-angle2))
            distance = self.loop.size/360 * (angle)
        else:
            angle2 = self.switch.angle

            if type(a_switch) is switch.Switch:
                if a_switch.loop.uuid == self.loop.uuid:
                    angle1 = a_switch.angle_my_loop
                else:
                    angle1 = a_switch.angle_other_loop
            else:
                angle1 = a_switch.angle

            angle = min(360-abs(angle1-angle2), abs(angle1-angle2))
            distance = self.loop.size/360 * (angle)

        if self.distance_to_next_node[0] == -1:
            self.distance_to_next_node[0] = distance
        else:
            self.distance_to_next_node[1] = distance


def get_node_id(switch, loop):
    for a_node in _nodes:
        if a_node.switch.uuid == switch.uuid and a_node.loop.uuid == loop.uuid:
            return a_node.id
    return -1
