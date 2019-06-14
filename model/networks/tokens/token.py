class Token:
    def __init__(self, source, destination):
        self._source = source
        self._destination = destination

    @property
    def source(self):
        return self._source

    @property
    def destination(self):
        return self._destination

    def serialize(self):
        return {
            'source': self.source,
            'destination': self.destination
        }
