class Rule:
    def __init__(self,destination=None,priority=0,switch_state=None,id_pod=None,time=None,empty=None,num_rule=None,change=None):
        self.destination = destination
        self.priority = priority
        self.switch_state = switch_state
        self.id_pod = id_pod
        self.time = time
        #self.num_rule = num_rule
        self.change = change
        self.empty = empty