class Token:
    def __init__(self, source=None, destination=None):
        source = source or None
        destination = destination or None
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
            "source": self.source.to_element_of_loop(),
            "destination": self.destination.to_element_of_loop()
        }
