class Rule:
    def __init__(self, switch_id, loop_id, destination=None, priority=None, empty=None, change=None, id_pod=None, time=None, num_rule=None):
        self.destination = destination
        self.priority = priority
        self.empty = empty
        self.loop_id = loop_id
        self.switch_id = switch_id
        #self.id_pod = id_pod
        #self.time = time
        #self.num_rule = num_rule
        self.change = change
        
    def match(self, switch_id, loop_id, destination=None, priority=None, empty=None, id_pod=None, time=None):
        """
        :return: true if the rule matches
        """
        #id_pod et time à ajouter si on s'en sert finalement
        if(switch_id == self.switch_id and self.loop_id == loop_id):
            if (destination is not None and destination == self.destination) or self.destination is None:
                if (priority is not None and priority == self.priority) or self.priority is None:
                    if (empty is not None and empty == self.empty) or self.empty is None:
                            return True
        return False

