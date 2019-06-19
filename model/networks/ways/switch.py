"""
réuni des connexions pour former les switchs du réseau
"""

from .way import Way


class Switch(Way):

    def __init__(self, id, route_in, route_out, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.route_in = route_in
        self.route_out = route_out

    @property
    def pods(self):
        return self.route_in.pods + self.route_out.pods

    def serialize(self):
        return super().serialize().update({
            'type': 'switch',
            'pods': self.pods
        })
