"""
1ere possibilité de noeud
Représentation de la portion de voie entre deux boucles (la voie qui est entre deux switchs de boucles différentes)
"""

from .line import Line


class Bridge(Line):
    def __init__(self, path):
        super().__init__()
        self._route = None
        self.path = path

    def serialize(self):
        return super().serialize().update({
            "type": "bridge"
        })
