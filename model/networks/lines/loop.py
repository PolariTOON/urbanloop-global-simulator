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
        return [pod for route in self._routes for pod in route.pods]

    def serialize(self):
        elements = []
        sections = []
        pods = []
        switches = self._switches
        routes = self._routes
        length = 0
        for way_index in range(len(switches)):
            switch = switches[way_index]
            switch = switch.serialize()
            elements.append(switch)
            route = routes[way_index]
            for step_index in range(len(route.steps)):
                step = route.steps[step_index]
                step = step.serialize()
                elements.append(step)
                section = route.sections[step_index]
                for pod_index in range(len(section.pods)):
                    pod = section.pods[pod_index]
                    position = pod.position + length
                    pod = pod.serialize()
                    pod.update({
                        "position": position,
                        "x": 0,  # TODO
                        "y": 0  # TODO
                    })
                    pods.append(pod)
                length += section.length
                section = section.serialize()
                sections.append(section)
            # On n'oublie pas la dernière section
            section = route.sections[-1]
            for pod_index in range(len(section.pods)):
                pod = section.pods[pod_index]
                position = pod.position + length
                pod = pod.serialize()
                pod.update({
                    "position": position,
                    "x": 0,  # TODO
                    "y": 0  # TODO
                })
                pods.append(pod)
            section = section.serialize()
            sections.append(section)
        dict = super().serialize()
        dict.update({
            "elements": elements,
            "sections": sections,
            "pods": pods
        })
        return dict
