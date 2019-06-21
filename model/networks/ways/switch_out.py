"""
réuni des connexions pour former les switchs du réseau
"""
from .switch import Switch


class SwitchOut(Switch):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        self._switch_in = None

        # Liaison de la route et des sections du pont
        self._beside.previous = self
        self._beside.sections[0].previous = self
        # Liaison inter aiguillage
        if self._beside.sections[-1].next is not None:
            self._switch_out = self._beside.sections[-1].next
            self._beside.sections[-1].next.switch_in = self

    @property
    def switch_in(self):
        return self._switch_in

    @switch_in.setter
    def switch_in(self, value):
        self._switch_in = value

    def serialize(self):
        return super().serialize().update({
            'type': 'switch_out'
        })
