class Token:
    def __init__(self, depart, destination):
        self.depart = depart
        self.destination = destination

    def serialize(self):
        return {
            'jsonType': 'token',
            'depart': self.depart,
            'destination': self.destination
        }
