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
        self._previous_route = None
        self._next_route = None


    @property
    def pods(self):
        return self._pods

    @property
    def previous_route(self):
        return self._previous_route

    @previous_route.setter
    def previous_route(self, value):
        self._previous_route = value

    @property
    def next_route(self):
        return self._next_route

    @next_route.setter
    def next_route(self, value):
        self._next_route = value

    def serialize(self):
        return super().serialize().update({
            'type': 'switch',
            'pods': self.pods
        })
