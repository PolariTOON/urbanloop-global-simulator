import Model.Global
import Model.Routing

TIMER_OTHER = 60
MY_TIMER = 40

class Switch:
    # network
    network = None
    is_routing_to_loop = False

    '''my_loop = None
    next_loop = None 
    size = 0 
    permanent_table = None'''

    def __init__(self, loop, other_loop, size):
        self.id = Model.Global.switch_id
        Model.Global.switch_id += 1
        self.my_loop = loop
        self.switched_loop = other_loop
        self.size = size
        self.permanent_table = {self.my_loop: [False, 0, [self.id, self.my_loop]],
                           self.switched_loop: [True, self.size, [self.id, self.switched_loop]]}
        self.table = Model.Routing.parcours(self, self.permanent_table, {self.my_loop: self.id, self.switched_loop: self.id} )
        # FINAL
        self.permanent_table = self.table
        self.defects = [[TIMER_OTHER] for i in range(0, Model.Global.switch_id)]
        self.defects[self.id] = MY_TIMER
        self.defects = [[False, False] for i in range(0, Model.Global.switch_id)]
        # anomalies des switches : [boucle presente, boucle aiguillee] True ==> anomalies

    def _change_state(self):
        self.isRoutingToLoop = not self.is_routing_to_loop
        return

    def route_capsule_to_station(self, capsule, station):
        # TODO
        return
