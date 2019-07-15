"""
réuni des connexions pour former les switchs du réseau
"""
from .switch import Switch


class SwitchOut(Switch):
    def __init__(self, env, id, **kwargs):
        super().__init__(env, id, **kwargs)
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

    @property
    def name(self):
        return "switchOut"

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "name": self.name,
            "type": "switch_out"
        })
        return dict
