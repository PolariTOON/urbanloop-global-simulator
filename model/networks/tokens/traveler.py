from .token import Token


class Traveler(Token):
    def __init__(self, source, destination):
        super().__init__(source, destination)

    def serialize(self):
        return super().serialize().update({})
