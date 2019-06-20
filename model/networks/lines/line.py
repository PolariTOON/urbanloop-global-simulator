class Line:
    def __init__(self, name=None):
        self._name = name or ""

    @property
    def name(self):
        return self._name

    def serialize(self):
        return {
            "name": self.name
        }
