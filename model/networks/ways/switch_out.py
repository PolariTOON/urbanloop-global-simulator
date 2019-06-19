"""
réuni des connexions pour former les switchs du réseau
"""

from .switch import Switch


class SwitchOut(Switch):
    def __init__(self, id, route_in, route_out, route_bridge):
        super().__init__(id, route_in, route_out)
        self._switch_in = None
        self._pods_loop_in = []
        self._pods_loop_out = []
        self._pods_bridge_out = []
        self._bridge_out = route_bridge

    @property
    def pods(self):
        return self._pods_loop_in + self._pods_loop_out + self._pods_bridge_out

    def serialize(self):
        return super().serialize().update({
            'type': 'out',
            'pods': self.pods
        })
