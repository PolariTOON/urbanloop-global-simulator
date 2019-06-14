"""
2eme possibilité de noeud
Une route est à la fois un noeud du meta-graphe et un sous-graphe divisé en sections, stations, garages séparés par des capteurs
"""

from .road import Road


class Route(Road):
    def __init__(self):
        super().__init__(self)
        self._sections = []
        self._steps = []

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
