"""
réuni des connexions pour former les switchs du réseau
"""
from .switch import Switch


class SwitchIn(Switch):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)
        self._switch_out = None

        # Liaison de la route et des sections du pont
        self._beside.next = self
        self._beside.sections[-1].next = self
        # Liaison inter aiguillage
        if self._beside.sections[0].previous is not None:
            self._switch_out = self._beside.sections[0].previous
            self._beside.sections[0].previous.switch_in = self

    @property
    def switch_out(self):
        return self._switch_out

    @switch_out.setter
    def switch_out(self, value):
        self._switch_out = value

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "type": "switch_in"
        })
        return dict
