"""
réuni des connexions pour former les switchs du réseau
"""

from .switch import Switch


class SwitchOut(Switch):
    def __init__(self, id, route_in, route_out, route_bridge, **kwargs):
        super().__init__(id, route_in, route_out, **kwargs)
        self._switch_in = None
        self._capsules_loop_in = []
        self._capsules_loop_out = []
        self._capsules_bridge_out = []
        self._bridge_out = route_bridge

    @property
    def capsules(self):
        return self._capsules_loop_in + self._capsules_loop_out + self._capsules_bridge_out

    def serialize(self):
        return super().serialize().update({
            'type': 'out',
            'capsules': self.capsules
        })
