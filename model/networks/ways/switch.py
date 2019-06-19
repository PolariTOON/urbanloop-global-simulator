"""
réuni des connexions pour former les switchs du réseau
"""

from .way import Way


class Switch(Way):
    def __init__(self):
        super().__init__()

    def serialize(self):
        return super().serialize().update({})
