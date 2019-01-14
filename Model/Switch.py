import Model.Routing

switch_id = 0

class Switch:
    # network
    network = None
    is_routing_to_loop = False

    '''my_loop = None
    next_loop = None 
    size = 0 
    permanent_table = None'''

    def __init__(self, loop, other_loop, size):
        global switch_id
        self.id = switch_id
        switch_id += 1
        self.my_loop = loop
        self.switched_loop = other_loop
        self.size = size
        self.permanent_table = {self.my_loop: [False, 0, [self.id, self.my_loop]],
                           self.switched_loop: [True, self.size, [self.id, self.switched_loop]]}
        self.table = Model.Routing.parcours(self.permanent_table, {self.my_loop: self.id, self.switched_loop: self.id} )
        # FINAL
        self.permanent_table = self.table

    def _change_tate(self):
        self.isRoutingToLoop = not self.is_routing_to_loop
        return

    def route_capsule_to_station(self, capsule, station):
        # TODO
        return
