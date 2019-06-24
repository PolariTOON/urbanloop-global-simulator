"""
Réunis des routes pour former les boucles du réseau
"""

from .line import Line


class Loop(Line):
    def __init__(self, id, routes=None, switches=None, **kwargs):
        super().__init__(id, **kwargs)
        self._routes = routes
        self._switches = switches

    @property
    def routes(self):
        return self._routes

    @property
    def pods(self):
        return [p for p in self._routes.pods]

    def serialize(self):
        elements = []
        sections = []
        pods = []
        switches = self._switches
        routes = self._routes
        for way_index in range(len(switches)):
            switch = switches[way_index]
            route = routes[way_index]
            elements.append(switch.serialize())
            for step_index in range(len(route.steps)):
                step = route.steps[step_index]
                section = route.sections[step_index]
                elements.append(step.serialize())
                sections.append(section.serialize())
                for pod_index in range(len(section.pods)):
                    pod = section.pods[pod_index]
                    pods.append(pod.serialize())
            # On n'oublie pas la dernière section
            section = route.sections[-1]
            sections.append(section.serialize())
            for pod_index in range(len(section.pods)):
                pod = section.pods[pod_index]
                pods.append(pod.serialize())
        dict = super().serialize()
        dict.update({
            "elements": elements,
            "sections": sections,
            "pods": pods
        })
        return dict
