import numpy as np


class Graph:

    def __init__(self):
        self.size = station.get_stations.size + switch.get_switches.size * 2 + warehouse.get_warehouses.size
        self.nodes = [None] * size

        """
        self.matrix = np.zeros(self.size, self.size)
        self.expected_matrix = np.zeros(self.size, self.size)
        """


    def add_edge(self, node1, node2, weight):
        self.matrix[node1][node2] = weight
        self.expected_matrix[node1][node2] = weight

    def delete_edge(self,node1,node2):
        self.matrix[node1][node2] = 0

    def get_edge_existence(self, node1, node2):
        if self.matrix[node1][node2] == 0:
            return False
        if self.matrix[node1][node2] == 1:
            return True

    def get_edge_weight(self, node1, node2):
        return self.matrix[node1][node2]

    def update_weight(self, node1, node2, new_weight):
        self.matrix[node1][node2] =self.matrix[node1][node2]

    def disable_way(self, node1, node2):
        self.matrix[node1][node2] = inf