"""
réuni des connexions pour former les switchs du réseau
"""
from .switch import Switch


class SwitchIn(Switch):
    def __init__(self, id, pods, route_in, route_out, route_bridge, **kwargs):
        super().__init__(id, pods, route_in, route_out, **kwargs)
        self._switch_out = None
        self._pods_loop_in = []
        self._pods_bridge_in = []
        self._pods_loop_out = []
        self._bridge_in = route_bridge

    @property
    def pods(self):
        return self._pods

    def serialize(self):
        return super().serialize().update({
            'type': 'in',
            'pods': self.pods
        })
