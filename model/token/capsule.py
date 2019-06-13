from model.graph.token import Token


class Capsule(Token):
    def __init__(self, travelers=None):
        self.travelers = travelers

    def serialize(self):
        return super().serialize().update({
            'jsonType': 'capsule',
            'travelers': self.travelers
        })
