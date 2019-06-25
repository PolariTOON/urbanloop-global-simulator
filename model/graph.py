from math import *

from model import node, station, warehouse
from model import switch
from model.node import Node
from settings import config


class Graph:

    def __init__(self, warehouses, stations, switches):
        self.size = len(stations) + len(switches) * 2 + len(warehouses)
        self.nodes = [] * self.size
        self.matrix = [[inf for j in range(self.size)] for i in range(self.size)]
        self.expected_matrix = [[inf for j in range(self.size)] for i in range(self.size)]

        self.init_nodes(warehouses, stations, switches)
        self.init_next_nodes(warehouses, stations)
        self.init_matrices()

    def init_nodes(self, warehouses, stations, switches):
        """ On créé les noeuds à partir des stations, switchs, warehouse du réseau """
        for a_station in stations:
            a = Node(a_station, a_station.loop)
            self.nodes.append(a)

        for a_warehouse in warehouses:
            a = Node(a_warehouse, a_warehouse.loop)
            self.nodes.append(a)

        for a_switch in switches:
            node1 = Node(a_switch, a_switch.my_loop)
            node2 = Node(a_switch, a_switch.other_loop)

            node1.add_next_node(node2)

            self.nodes.append(node1)
            self.nodes.append(node2)

    def init_next_nodes(self, warehouses, stations):
        for a_node in self.nodes:
            if type(a_node.elt) is station.Station or type(a_node.elt) is warehouse.Warehouse:
                a_node.add_next_node(self.nodes[node.get_node_id(a_node.elt.next_element, a_node.loop)])
            elif a_node.elt.loop.uuid == a_node.loop.uuid:  # Le noeud est un switch sur la boucle actuelle
                a_node.add_next_node(self.nodes[node.get_node_id(a_node.elt.next_element, a_node.elt.loop)])
            else:  # Le noeud est un switch sur la boucle aiguillée
                a_node.add_next_node(self.nodes[node.get_node_id(a_node.elt.next_element_other, a_node.elt.other_loop)])

    def init_matrices(self):
        #speed : unités à vérifier
        """
        On créé le graphe qui représente le réseau
        """
        speed = float(config.capsule['max_speed'])
        for node in self.nodes:
            self.matrix[node.id][node.next_nodes[0].id] = node.distance_to_next_node[0] / speed
            self.expected_matrix[node.id][node.next_nodes[0].id] = node.distance_to_next_node[0] / speed
            if node.next_nodes[1] is not None:
                self.matrix[node.id][node.next_nodes[1].id] = node.distance_to_next_node[1] / speed
                self.expected_matrix[node.id][node.next_nodes[1].id] = node.distance_to_next_node[1] / speed

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

        self.matrix[node1][node2] = (1 - 0.125) * self.matrix[node1][node2] + 0.125 * sample_time

        return self.matrix[node1][node2] > 3 * self.expected_matrix[node1][node2]

    def no_more_congestion(self, previous_switch, current_switch, sample_time):
        node1 = node.get_node_id(previous_switch, previous_switch.loop)

        if previous_switch.uuid == current_switch.uuid:
            node2 = node.get_node_id(previous_switch, previous_switch.other_loop)
        else:
            node2 = node.get_node_id(current_switch, current_switch.loop)

        return self.matrix[node1][node2] < 2 * self.expected_matrix[node1][node2]

    def calcul(self, node_start, node_arrival):
        """
        calcul du chemin optimal entre un noeud (switch, warehouse, station) et une destination
        Il s'agit d'un Dijkstra.
        :param node_arrival: destination OBLIGATOIRE
        :param  node_start : depart OBLIGATOIRE
        :return: path : le chemin optimal : liste ordonnée (sens croissant) des noeuds traversés pour aller du départ à
        la destination
    """
        distance = self.size * [inf]
        distance[node_start.id] = 0

        VISITED = inf
        visited_nodes = [-1] * self.size

        predecessor = self.size * [None]

        def maj_distances(node1, node2):
            poids12 = self.get_edge_weight(node1.id, node2.id)
            if distance[node2.id] > distance[node1.id] + poids12:
                distance[node2.id] = distance[node1.id] + poids12
                predecessor[node2.id] = node1
                for i in range(len(visited_nodes)):
                    if visited_nodes[i] == node2.id:
                        visited_nodes[i] = -1

        def f(node, pred_Node):
            # Initialisation
            if pred_Node is None:
                visited_nodes[node.id] = VISITED

                for n in node.next_nodes:
                    if n is not None:
                        maj_distances(node, n)

                for n in node.next_nodes:
                    if n is not None:
                        f(n, node)

            elif visited_nodes[node.id] < VISITED and visited_nodes[node.id] != pred_Node.id:
                if visited_nodes[node.id] == -1:
                    visited_nodes[node.id] = pred_Node.id
                elif visited_nodes[node.id] < VISITED:
                    visited_nodes[node.id] = VISITED

                for n in node.next_nodes:
                    if n is not None:
                        maj_distances(node, n)

                for n in node.next_nodes:
                    if n is not None:
                        f(n, node)

        f(node_start, None)
        path = list()
        current_node = node_arrival
        while predecessor[current_node.id] is None:
            current_node = current_node.previous_nodes[0]
        while current_node.id != node_start.id:
            path.append(current_node)
            current_node = predecessor[current_node.id]

        path.append(node_start)
        return path

    def change(self, node_start, node_dest):
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
            if type(node.elt) is switch.Switch:
                list_nodes.append(node)
        return list_nodes

    def get_node_from_elt(self, elt):
        """
        :param elt: switch/garage/station dont on veut récupérer le noeud
        dans le graphe
        :return: le noeud du graphe où apparaît l'élément
        """
        for node in self.nodes:
            if node.elt.uuid == elt.uuid:
                return node
        return None
