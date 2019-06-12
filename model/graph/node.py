class Node:
    def __init__(self):
        pass

    @property
    def capsules(self):
        raise NotImplementedError

    def serialize(self):
        return {
            'jsonType': 'node'
        }
