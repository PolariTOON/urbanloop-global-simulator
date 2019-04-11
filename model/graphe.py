import numpy as np


class Graph:

    def __init__(self, node_list):
        self.nodeList = node_list
        self.size = len(node_list)
        self.matrix = np.zeros(self.size)

    def add_edge(self, node1, node2, weight):
        self.matrix[node1][node2] = weight

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

    def disable_way(self, node):
        self.matrix[node-1][node] = inf


