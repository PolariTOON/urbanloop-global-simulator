"""
réuni des connexions pour former les switchs du réseau
"""

from .way import Way


class Switch(Way):

    def __init__(self, id, loop_in=None, loop_out=None, route_bridge=None, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self._previous = loop_in
        self._next = loop_out
        self._beside = route_bridge

        # Liaison des routes et sections de la boucle à l'aiguillage
        # Route précédente
        self._previous.next_switch = self
        self._previous.sections[-1].next = self
        # Route suivante
        self._next.previous_switch = self
        self._next.sections[0].previous = self

    @property
    def beside(self):
        return self._beside

    @beside.setter
    def beside(self, value):
        self._beside = value

    @property
    def next(self):
        return self._next

    @next.setter
    def next(self, value):
        self._next = value

    @property
    def previous(self):
        return self._previous

    @previous.setter
    def previous(self, value):
        self._previous = value

    def serialize(self):
        return super().serialize().update({
            'type': 'switch',
            'pods': self.pods
        })

    @property
    def pods(self):
        return  # TODO
