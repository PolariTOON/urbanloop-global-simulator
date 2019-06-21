"""
réuni des connexions pour former les switchs du réseau
"""
from .switch import Switch


class SwitchIn(Switch):
    def __init__(self, id, pods=None, **kwargs):
        super().__init__(id, **kwargs)
        self._switch_out = None
        self._pods_loop_in = pods["loop_in"] or []
        self._pods_bridge_in = pods["bridge"] or []
        self._pods_loop_out = pods["loop_out"] or []

        # Liaison de la route et des sections du pont
        self._beside.next = self
        self._beside.sections[-1].next = self
        # Liaison inter aiguillage
        if self._beside.sections[0].previous is not None:
            self._switch_out = self._beside.sections[0].previous
            self._beside.sections[0].previous.switch_in = self

    @property
    def pods(self):
        return   # TODO

    @property
    def switch_out(self):
        return self._switch_out

    @switch_out.setter
    def switch_out(self, value):
        self._switch_out = value

    def serialize(self):
        return super().serialize().update({
            'type': 'in',
            'pods': self.pods
        })
