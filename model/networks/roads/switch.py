"""
réuni des connexions pour former les switchs du réseau
"""

from .road import Road


class Switch(Road):

    def __init__(self, id, route_in, route_out):
        super().__init__()
        self.id = id
        self.route_in = route_in
        self.route_out = route_out

    @property
    def capsules(self):
        return self.route_in.capsules + self.route_out.capsules

    def serialize(self):
        return super().serialize().update({
            'type': 'switch',
            'capsules': self.capsules
        })
