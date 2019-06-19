class Node:
    def __init__(self, name=None):
        self._name = name or ""

    @property
    def name(self):
        return self._name

    @property
    def pods(self):
        raise NotImplementedError

    def serialize(self):
        return {
            'pods': [pod.serialize() for pod in self.pods]
        }
