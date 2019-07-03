class Token:
    def __init__(self, source=None, destination=None, **kwargs):
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

    @destination.setter
    def destination(self, value):
        self._destination = value

    @source.setter
    def source(self, value):
        self._source = value

    def serialize(self):
        return {
            "source": self.source.to_element_of_loop(),
            "destination": self.destination.to_element_of_loop()
        }
