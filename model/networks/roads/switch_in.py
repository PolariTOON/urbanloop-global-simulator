"""
réuni des connexions pour former les switchs du réseau
"""

from .switch import Switch


class SwitchIn(Switch):
    def __init__(self):
        super().__init__(self)
        self._switch_out = None
        self._capsules_in_loop = []
        self._capsules_in_bridge = []
        self._capsules_out_loop = []

    @property
    def capsules(self):
        return self._capsules_in_loop + self._capsules_in_bridge + self._capsules_out_loop

    def serialize(self):
        return super().serialize().update({
            'type': 'in'
        })
