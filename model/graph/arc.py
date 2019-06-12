class Arc:
    def __init__(self, previous_node, next_node):
        self.previous_node = previous_node
        self.next_node = next_node

    def serialize(self):
        return {
            'jsonType': 'arc',
            'previous_node': self.previous_node,
            'next_node': self.next_node
        }
