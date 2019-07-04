from model import switch
from model import identifier

_nodes = []


class Node:

    def __init__(self, elt, loop):
        global _nodes
        _nodes.append(self)

        self.elt = elt
        self.loop = loop
        self.previous_nodes = [None] * 2
        self.next_nodes = [None] * 2
        self.distance_to_next_node = [-1] * 2
        self.id = identifier.generate_node_id()

    def add_next_node(self, node):
        node.add_previous_node(self)

        if self.next_nodes[0] is None:
            self.next_nodes[0] = node
        else:
            self.next_nodes[1] = node

        self.calculate_distance(node.elt)

    def add_previous_node(self, node):

        if self.previous_nodes[0] is None:
            self.previous_nodes[0] = node
        else:
            self.previous_nodes[1] = node

    def calculate_distance(self, elt_cible):
        """
        Calcule la longueur du troncon entre lui même et le switch/warehouse/station entré en paramètre
        :param elt_suivant: switch/warehouse/station d'arrivée du troncon dont on calcule la longeur
        :return: met jour l'attribut distance_to_next_node
        """
        if self.elt.uuid == elt_cible.uuid:
            distance = self.elt.size
        else:
            if type(elt_cible) is switch.Switch:
                # On gère le cas spécifique du switch en se plaçant sur la bonne boucle
                if elt_cible.loop.uuid == self.loop.uuid:
                    angle1 = elt_cible.angle_my_loop
                else:
                    angle1 = elt_cible.angle_other_loop
            else:
                angle1 = elt_cible.angle

            if type(self.elt) is switch.Switch:
                # On se place sur la bonne boucle
                if self.elt.loop.uuid == self.loop.uuid:
                    angle2 = self.elt.angle_my_loop
                else:
                    angle2 = self.elt.angle_other_loop
            else:
                angle2 = self.elt.angle

            # On prend la portion du cercle de la boucle entre les deux elts
            angle = min(360 - abs(angle1 - angle2), abs(angle1 - angle2))
            distance = self.loop.size / 360 * angle

        if self.distance_to_next_node[0] == -1:
            self.distance_to_next_node[0] = distance
        else:
            self.distance_to_next_node[1] = distance


def get_node_id(elt, loop):
    for a_node in _nodes:
        if a_node.loop.uuid == loop.uuid and a_node.elt.uuid == elt.uuid:
            return a_node.id
    return -1
