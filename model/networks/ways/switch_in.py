"""
réuni des connexions pour former les switchs du réseau
"""
from .switch import Switch


class SwitchIn(Switch):
    def __init__(self, id, route_in, route_out, route_bridge, **kwargs):
        super().__init__(id, route_in, route_out, **kwargs)
        self._switch_out = None
        self._pod_loop_in = []
        self._pod_bridge_in = []
        self._pod_loop_out = []
        self._bridge_in = route_bridge

    @property
    def pods(self):
        return self._pod_loop_in + self._pod_bridge_in + self._pod_loop_out

    def serialize(self):
        return super().serialize().update({
            'type': 'in',
            'pods': self.pods
        })
