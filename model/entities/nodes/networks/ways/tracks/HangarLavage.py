from .Hangar import Hangar


class HangarLavage(Hangar):
    """ Classe modélisant un hangar=dépôt de lavage"""
    def __init__(self, env, id, departure_pods=None, pods=None, element_of_loop=None, **kwargs):
        super().__init__(env, id, departure_pods, pods, element_of_loop, **kwargs)
