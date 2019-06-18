"""
1ere possibilité de noeud
Représentation de la portion de voie entre deux boucles (la voie qui est entre deux switchs de boucles différentes)
"""

from .line import Line


class Bridge(Line):
    def __init__(self, id_switch_in, id_switch_out, route, path):
        super().__init__()
        self._route = route
        self.path = path
        self.id_switch_out = id_switch_out
        self.id_switch_in = id_switch_in

    def serialize(self):
        return super().serialize().update({
            "type": "bridge"
        })
