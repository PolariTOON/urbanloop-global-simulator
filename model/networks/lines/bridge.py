"""
1ere possibilité de noeud
Représentation de la portion de voie entre deux boucles (la voie qui est entre deux switchs de boucles différentes)
"""

from .line import Line


class Bridge(Line):
    def __init__(self, id, routes=None, switches=None, **kwargs):
        super().__init__(id, **kwargs)
        self._routes = routes or []
        self._switches = switches or []

    def serialize(self):
        return super().serialize().update({
            "type": "bridge"
        })
