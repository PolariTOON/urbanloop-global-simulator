class Node:
    def __init__(self, name=None):
        self._name = name or ""

    @property
    def name(self):
        return self._name

    @property
    def capsules(self):
        raise NotImplementedError

    def serialize(self):
        return {
            'capsules': [capsule.serialize() for capsule in self.capsules]
        }
