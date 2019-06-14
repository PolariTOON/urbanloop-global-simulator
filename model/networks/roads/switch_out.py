"""
réuni des connexions pour former les switchs du réseau
"""

from .switch import Switch


class SwitchOut(Switch):
    def __init__(self):
        super().__init__(self)
        self._switch_in = None
        self._capsules_in_loop = []
        self._capsules_out_loop = []
        self._capsules_out_bridge = []

    @property
    def capsules(self):
        return self._capsules_in_loop + self._capsules_out_loop + self._capsules_out_bridge

    def serialize(self):
        return super().serialize().update({
            'type': 'out'
        })
