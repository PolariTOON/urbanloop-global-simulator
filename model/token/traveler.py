from model.graph.token import Token


class Traveler(Token):
    def __init__(self):
        pass

    def serialize(self):
        return super().serialize().update({
            'jsonType': 'traveler'
        })
