from .token import Token
import uuid


class Pod(Token):
    def __init__(self, source, destination, travelers):
        super().__init__(source, destination)
        self.id = uuid.uuid4().hex  # génération d'un identifiant unique
        self._travelers = travelers if travelers is not None else []

    @property
    def travelers(self):
        return self._travelers

    def serialize(self):
        return super().serialize().update({
            'travelers': [traveler.serialize() for traveler in self.travelers]
        })
