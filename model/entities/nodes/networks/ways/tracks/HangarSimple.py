from .Hangar import Hangar


class HangarSimple(Hangar):
    """ Classe modélisant un dépôt, y est géré le départ des capsules, le réapprovisionnement et
    les interactions avec les autres éléments du réseau"""

    def __init__(self, env, id, departure_pods=None, pods=None, element_of_loop=None, **kwargs):
        super().__init__(env, id, departure_pods, pods, element_of_loop, **kwargs)
