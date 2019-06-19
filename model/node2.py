class Node:
    def __init__(self):
        pass

    @property
    def pods(self):
        raise NotImplementedError

    def serialize(self):
        return {
            'pods': [pod.serialize() for pod in self.pods]
        }
