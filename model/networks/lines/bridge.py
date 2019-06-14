"""
1ere possibilité de noeud
Représentation de la portion de voie entre deux boucles (la voie qui est entre deux switchs de boucles différentes)
"""

from . import Line


class Bridge(Line):
    def __init__(self):
        super().__init__(self)
        self._route = None

    def serialize():
        return super().serialize().update({})
