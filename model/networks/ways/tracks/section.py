"""
Possibilité de noeud du sous-graphe désignant une section de route
"""
from ...tokens.pod import Pod
from .track import Track


class Section(Track):
    def __init__(self, previous_track, next_track, path, **kwargs):
        super().__init__(previous_track, next_track, **kwargs)
        self._len = None  # taille de la section
        self._path = path

    @property
    def len(self):
        return self._len

    @property
    def path(self):
        return self._path

    def serialize(self):
        return super().serialize().update({
            'len': self.len,
            'path': self.path
        })

    def add_pod(self, id, source, destination, travelers):
        self.pods.append(Pod(id, source, destination, travelers))
