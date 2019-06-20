"""
réuni des connexions pour former les switchs du réseau
"""

from .way import Way


class Switch(Way):

    def __init__(self, id, pods, route_in, route_out, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.route_in = route_in
        self.route_out = route_out
        self._pods = pods

    @property
    def pods(self):
        return self._pods

    def serialize(self):
        return super().serialize().update({
            'type': 'switch',
            'pods': self.pods
        })
