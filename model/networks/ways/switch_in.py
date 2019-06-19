"""
réuni des connexions pour former les switchs du réseau
"""

from .switch import Switch


class SwitchIn(Switch):
    def __init__(self, id, route_in, route_out, route_bridge, **kwargs):
        super().__init__(id, route_in, route_out, **kwargs)
        self._switch_out = None
        self._capsules_loop_in = []
        self._capsules_bridge_in = []
        self._capsules_loop_out = []
        self._bridge_in = route_bridge

    @property
    def capsules(self):
        return self._capsules_loop_in + self._capsules_bridge_in + self._capsules_loop_out

    def serialize(self):
        return super().serialize().update({
            'type': 'in',
            'capsules': self.capsules
        })
