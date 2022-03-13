from .Hangar import Hangar
from .shed import Shed


class HangarRevision(Hangar):
    def __init__(self, env, id, departure_pods=None, pods=None, element_of_loop=None, **kwargs):
        super().__init__(env, id, departure_pods, pods, element_of_loop, **kwargs)
