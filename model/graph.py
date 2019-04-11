import numpy as np
from math import *


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
        if self.matrix[node1][node2] == inf:
            return False
        else:
            return True

    def get_edge_weight(self, node1,node2):
        return self.matrix[node1][node2]

    def update_weight(self, node1, node2, sample_rtt):
        self.matrix[node1][node2] =(1-0.125)*self.matrix[node1][node2]+0.125*sample_rtt

    def calcul (self, node_start, node_arrival):
        """Dijkstra et ça marche"""

    def change (node_start, node_dest):
        if node_start.next_node2 == node_dest:
           return False
        else:
            return True
