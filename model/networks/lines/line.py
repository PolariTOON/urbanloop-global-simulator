class Line:
    def __init__(self, id, name=None, **kwargs):
        self._id = id
        self._name = name or ""

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    def serialize(self):
        return {
            "name": self._name
        }

    @property
    def pods(self):
        raise NotImplementedError
