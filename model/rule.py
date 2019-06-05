class Rule:
    def __init__(self, switch_id, loop_id, destination=None, priority=None, empty=None, change=None):
        self.destination = destination
        self.priority = priority
        self.empty = empty
        self.loop_id = loop_id
        self.switch_id = switch_id
        self.change = change

    def match(self, switch_id, loop_id, destination=None, priority=None, empty=None):
        """
        :return: true if the rule matches
        """
        if switch_id == self.switch_id and self.loop_id == loop_id:
            if (destination is not None and destination == self.destination) or self.destination is None:
                if (priority is not None and priority == self.priority) or self.priority is None:
                    if (empty is not None and empty == self.empty) or self.empty is None:
                        return True
        return False
