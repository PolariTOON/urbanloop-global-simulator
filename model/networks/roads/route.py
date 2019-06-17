"""
2eme possibilité de noeud
Une route est à la fois un noeud du meta-graphe et un sous-graphe divisé en sections, stations, garages séparés par des capteurs
"""

from .road import Road


class Route(Road):
    def __init__(self, tracks):
        super().__init__()
        self._sections = []
        self._steps = []
        self.build(tracks)

    @property
    def capsules(self):
        return [capsule for section in self.sections for capsule in section.capsules] + [capsule for step in self.steps for capsule in step.capsules]

    @property
    def sections(self):
        return self._sections

    @property
    def steps(self):
        return self._steps

    def serialize(self):
        return super().serialize().update({
            'type': 'route'
        })

    def build(self, tracks):
        #  TODO : contruction de la route à partir des tracks la composant
        for track in tracks:
            pass
