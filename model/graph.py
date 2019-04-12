import numpy as np
from math import *

from model import warehouse, node
from model import switch
from model import station
from model.node import Node
from model.station import get_stations
from model.switch import get_switches
from model.warehouse import get_warehouses
from settings import config


class Graph:

    def __init__(self):
        self.size = len(station.get_stations()) + len(switch.get_switches()) * 2 + len(warehouse.get_warehouses())
        self.nodes = [None] * self.size
        self.matrix = np.zeros(self.size, self.size)
        self.expected_matrix = np.zeros(self.size, self.size)

        self.init_nodes()
        self.init_next_nodes()
        self.init_matrices()

    def init_nodes(self):
        for station in get_stations():
            self.nodes.append(Node(station, station.loop))

        for warehouse in get_warehouses():
            self.nodes.append(Node(warehouse, warehouse.loop))

        for switch in get_switches():
            node1 = Node(switch, switch.my_loop)
            node2 = Node(switch, switch.other_loop)

            node1.add_next_node(node2)

            self.nodes.append(node1)
            self.nodes.append(node2)

    def init_next_nodes(self):
        for node in self.nodes:
            if station.get_stations().count(node.switch) > 0 or warehouse.get_warehouses().count(node.switch) > 0:
                node.add_next_node(self.nodes[node.get_node_id(node.switch.next_element), node.loop])
            elif node.switch.next_element.loop.uuid != node.loop.uuid:
                node.add_next_node(self.nodes[node.get_node_id(node.switch.next_element_other, node.loop)])
            else:
                node.add_next_node(self.nodes[node.get_node_id(node.switch.next_element, node.loop)])

    def init_matrices(self):
        #speed : unités à vérifier
        speed = float(config.capsule['max_speed'])
        for node in self.nodes:
            self.matrix[node.id][node.next_nodes[0].id] = node.distance_to_next_node[0]/speed
            self.expected_matrix[node.id][node.next_nodes[0].id] = node.distance_to_next_node[0]/speed
            if node.next_nodes[1] is not None:
                self.matrix[node.id][node.next_nodes[1].id] = node.distance_to_next_node[1]/speed
                self.expected_matrix[node.id][node.next_nodes[0].id] = node.distance_to_next_node[0]/speed


    def add_edge(self, node1, node2, weight):
        self.matrix[node1][node2] = weight

    def delete_edge(self,node1,node2):
        self.matrix[node1][node2] = 0

    def get_edge_existence(self, node1, node2):
        return self.matrix[node1][node2] > 0

    def get_edge_weight(self, node1,node2):
        return self.matrix[node1][node2]

    def update_weight(self, previous_switch, current_switch, sample_time):
        """
         fonction qui met à jour le poids sur le tronçon qui vient d'être parcouru par une capsule
         :param  previous_switch: le dernier switch que la capsule a parcouru (début du tronçon)
         :param  current_switch: le switch qui a routé la capsule (fin du tronçon)
         :param  sample_time: le temps qu'a mis la capsule pour parcourir le tronçon
         :return: True si il y a congestion, False sinon (boolean)
        """
        node1 = node.get_node_id(previous_switch, previous_switch.loop)

        if previous_switch.uuid == current_switch.uuid:
            node2 = node.get_node_id(previous_switch, previous_switch.other_loop)
        else:
            node2 = node.get_node_id(current_switch, current_switch.loop)

        self.matrix[node1][node2] = (1-0.125)*self.matrix[node1][node2]+0.125*sample_time

        return self.matrix[node1][node2] > 3 * self.expected_matrix[node1][node2]

    def calcul(self, node_start, node_arrival):
        distance_min = self.size * [inf]
        non_visited_node = list(self.nodes)
        current_node = node_start
        distance_min[current_node.id] = 0
        non_visited_node.remove(current_node)
        while non_visited_node.size() is not None:
            for next_node in self.matrix[current_node.id]:
                if not (next_node in non_visited_node):
                    distance_min[next_node.id] = min(distance_min[next_node.id], distance_min[current_node.id]
                                                     + self.get_edge_weight(current_node, next_node))
            next_min = inf
            next = None
            for next_node in non_visited_node:
                if distance_min[next_node.id] <= next_min:
                    next_min = distance_min[next_node.id]
                    next = next_node
            current_node = next
            non_visited_node.remove(current_node)

        path = []
        while current_node is not node_start:
            path = [current_node] + path
            pred_min = inf
            pred = None
            for predecessor in self.nodes:
                if self.get_edge_existence(predecessor, current_node):
                    if distance_min[predecessor.id] < pred_min:
                        pred_min = distance_min[predecessor.id]
                        pred = predecessor
            current_node = pred
        return [node_start] + path

    def change(node_start, node_dest):
        return node_start.loop.uuid != node_dest.loop.uuid

    def get_time_max(self, previous_switch, current_switch):
        node1 = node.get_node_id(previous_switch, previous_switch.loop)

        if previous_switch.uuid == current_switch.uuid:
            node2 = node.get_node_id(previous_switch, previous_switch.other_loop)
        else:
            node2 = node.get_node_id(current_switch, current_switch.loop)

        return 10 * self.expected_matrix[node1][node2]

    def disable_way(self, previous_switch, current_switch):
        node1 = node.get_node_id(previous_switch, previous_switch.loop)

        if previous_switch.uuid == current_switch.uuid:
            node2 = node.get_node_id(previous_switch, previous_switch.other_loop)
        else:
            node2 = node.get_node_id(current_switch, current_switch.loop)

        self.matrix[node1][node2] = inf
