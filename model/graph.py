import numpy as np
from math import *


class Graph:

    def __init__(self):
        self.size = station.get_stations.size + switch.get_switches.size * 2 + warehouse.get_warehouses.size
        self.nodes = [None] * size
        self.matrix = np.zeros(self.size, self.size)

    def add_edge(self, node1, node2, weight):
        self.matrix[node1][node2] = weight

    def delete_edge(self,node1,node2):
        self.matrix[node1][node2] = 0

    def get_edge_existence(self, node1, node2):
        if self.matrix[node1][node2] == inf:
            return False
        else:
            return True

    def get_edge_weight(self, node1,node2):
        return self.matrix[node1][node2]

    def update_weight(self, node1, node2, sample_rtt):
        self.matrix[node1][node2] = (1-0.125) * self.matrix[node1][node2] + 0.125*sample_rtt

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

    def change(self, node_start, node_dest):
        if node_start.next_node2 == node_dest:
            return False
        else:
            return True
