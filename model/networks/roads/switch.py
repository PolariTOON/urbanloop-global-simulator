"""
réuni des connexions pour former les switchs du réseau
"""

from .road import Road


class Switch(Road):
    def __init__(self):
        super().__init__(self)

    def serialize(self):
        return super().serialize().update({})
