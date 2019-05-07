import numpy as np
from math import *
import copy

from model import warehouse, node
from model import switch
from model import station
from model.node import Node
from settings import config


class Graph:

    def __init__(self):
        self.size = len(station.get_stations()) + len(switch.get_switches()) * 2 + len(warehouse.get_warehouses())
        self.nodes = [] * self.size
        self.matrix = [[inf for j in range(self.size)] for i in range(self.size)]
        self.expected_matrix = [[inf for j in range(self.size)] for i in range(self.size)]

        self.init_nodes()
        self.init_next_nodes()
        self.init_matrices()
        #self.delete_section(12)

    def init_nodes(self):
        for a_station in station.get_stations():
            self.nodes.append(Node(a_station, a_station.loop))

        for a_warehouse in warehouse.get_warehouses():
            self.nodes.append(Node(a_warehouse, a_warehouse.loop))

        for a_switch in switch.get_switches():
            node1 = Node(a_switch, a_switch.my_loop)
            node2 = Node(a_switch, a_switch.other_loop)

            node1.add_next_node(node2)

            self.nodes.append(node1)
            self.nodes.append(node2)

    def init_next_nodes(self):
        for a_node in self.nodes:
            if station.get_stations().count(a_node.switch) > 0 or warehouse.get_warehouses().count(a_node.switch) > 0:
                a_node.add_next_node(self.nodes[node.get_node_id(a_node.switch.next_element, a_node.loop)])
            elif a_node.switch.loop.uuid == a_node.loop.uuid:
                a_node.add_next_node(self.nodes[node.get_node_id(a_node.switch.next_element, a_node.switch.loop)])
            else:
                a_node.add_next_node(self.nodes[node.get_node_id(a_node.switch.next_element_other, a_node.switch.other_loop)])

    def init_matrices(self):
        #speed : unités à vérifier
        speed = float(config.capsule['max_speed'])
        for node in self.nodes:
            self.matrix[node.id][node.next_nodes[0].id] = node.distance_to_next_node[0]/speed
            self.expected_matrix[node.id][node.next_nodes[0].id] = node.distance_to_next_node[0]/speed
            if node.next_nodes[1] is not None:
                self.matrix[node.id][node.next_nodes[1].id] = node.distance_to_next_node[1]/speed
                self.expected_matrix[node.id][node.next_nodes[1].id] = node.distance_to_next_node[1]/speed


    def add_edge(self, node1, node2, weight):
        self.matrix[node1][node2] = weight

    def delete_edge(self,node1,node2):
        self.matrix[node1][node2] = inf

    def get_edge_existence(self, node1, node2):
        return self.matrix[node1][node2] < inf

    def get_edge_weight(self, node1, node2):
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
        """
        calcul du chemin optimal entre un noeud (switch, warehouse, station) et une destination
        :param node_arrival: destination OBLIGATOIRE
        :param  node_start : depart OBLIGATOIRE
        :return: path : le chemin optimal : liste ordonnée (sens croissant) des noeuds traversés pour aller du départ à
        la destination
    """
        distance = self.size * [inf]
        distance[node_start.id] = 0

        VISITED = self.size+100
        visited_nodes = [-1] * self.size

        predecessor = self.size * [None]

        def maj_distances(node1, node2):
            if(distance[node2.id] > distance[node1.id]+ self.get_edge_weight(node1.id,node2.id)):
                distance[node2.id] = distance[node1.id]+ self.get_edge_weight(node1.id,node2.id)
                predecessor[node2.id] = node1

        def f(node, pred_Node):
            if(pred_Node is None):
                visited_nodes[node.id]=VISITED

                for n in node.next_nodes:
                    if(n is not None):
                        maj_distances(node, n)

                for n in node.next_nodes:
                    if(n is not None):
                        f(n, node)

            elif(visited_nodes[node.id]<VISITED and visited_nodes[node.id]!=pred_Node.id):
                if(visited_nodes[node.id]==-1):
                    visited_nodes[node.id]=pred_Node.id
                elif(visited_nodes[node.id]<VISITED):
                    visited_nodes[node.id]=VISITED

                for n in node.next_nodes:
                    if(n is not None):
                        maj_distances(node, n)

                for n in node.next_nodes:
                    if(n is not None):
                        f(n, node)

        f(node_start,None)

        path = list()
        current_node = node_arrival
        while(current_node.id != node_start.id):
            path.append(current_node)
            current_node = predecessor[current_node.id]

        path.append(node_start)
        return path


    def delete_section(self,id):
        for i in range(self.size):
            self.matrix[id][i]=inf;




    def change(node_start, node_dest):
        return node_start.loop.uuid != node_dest.loop.uuid

    def get_time_max(self, previous_switch, current_switch):
        """
        Retourne le temps à partir duquel on considère un troncon comme coupé. On prends comme limite
        10 * le temps de parcours en conditions normales
        :param previous_switch: switch, warehouse ou station d'où commence le troncon
        :param current_switch: switch, warehouse ou station où arrive le troncon
        :return: temps à partir duquel on considère un troncon comme coupé
        """
        node1 = node.get_node_id(previous_switch, previous_switch.loop)

        if previous_switch.uuid == current_switch.uuid:
            node2 = node.get_node_id(previous_switch, previous_switch.other_loop)
        else:
            node2 = node.get_node_id(current_switch, current_switch.loop)

        return 10 * self.expected_matrix[node1][node2]

    def disable_way(self, previous_switch, current_switch):
        """
        Coupe un troncon entre deux noeuds. Concretement cela place la valeur inf (infini) comme poids de l'arc
        dans le graphe
        :param previous_switch: switch, warehouse ou station d'où commence le troncon
        :param current_switch: switch, warehouse ou station où arrive le troncon
        """

        node1 = node.get_node_id(previous_switch, previous_switch.loop)

        if previous_switch.uuid == current_switch.uuid:
            node2 = node.get_node_id(previous_switch, previous_switch.other_loop)
        else:
            node2 = node.get_node_id(current_switch, current_switch.loop)

        self.matrix[node1][node2] = inf

    def get_switches_nodes(self):
    	list_nodes = list()
    	for node in self.nodes:
    		if type(node.switch) is switch.Switch:
    			list_nodes.append(node)
    	return list_nodes

    def get_node_from_switch(self, switch):
    	for node in self.nodes:
    		if node.switch.uuid == switch.uuid:
    			return node
    	return None

    def get_node_from_id(self, id):
        for node in self.nodes:
            if node.id == id:
                return node
        return None
