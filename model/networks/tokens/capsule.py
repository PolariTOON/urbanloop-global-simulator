from .token import Token


class Capsule(Token):
    def __init__(self, travelers=None):
        super().__init__()
        self._travelers = travelers if travelers is not None else []

    @property
    def travelers(self):
        return self._travelers

    def serialize(self):
        return super().serialize().update({
            'travelers': [traveler.serialize() for traveler in self.travelers]
        })
