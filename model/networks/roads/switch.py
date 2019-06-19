"""
réuni des connexions pour former les switchs du réseau
"""

from .road import Road


class Switch(Road):

    def __init__(self, id, route1, route2):
        super().__init__()
        self.id = id
        self.route1 = route1
        self.route2 = route2

    @property
    def capsules(self):
        return self.route1.capsules + self.route2.capsules

    def serialize(self):
        return super().serialize().update({
            'type': 'switch',
            'capsule': self.capsules
        })
