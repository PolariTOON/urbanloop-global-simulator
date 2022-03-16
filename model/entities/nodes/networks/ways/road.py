from math import inf

from .switch import Switch
from .tracks.HangarSimple import HangarSimple
from .tracks.HangarLavage import HangarLavage
from .tracks.HangarRevision import HangarRevision
from .tracks.section import Section
from .tracks.sensor import Sensor
from .tracks.shed import Shed
from .tracks.station import Station
from .way import Way



class Road(Way):
    """Classe modélisant une route du réseau, c'est une entitée intermédiaire au même niveau que les aiguillages
    Cette entité est aussi vue comme un sous graphe."""
    #p
    count = 0

    def __init__(self, env, id, margin_min, pod_size, is_bridge, steps=None, sections=None, **kwargs):
        super().__init__(env, id, pod_size, **kwargs)
        self._steps = steps or []  # sheds, capteurs et stations
        self._sections = sections or []  # [{"type": "machin"}, ...](le bon nombre = 1 de + que de steps)
        self._previous = None
        self._next = None
        self._is_bridge = is_bridge
        self._weight = 0
        #p
        print(f"Road{Road.count}")
        Road.count+=1
        for el in self._sections:
            print(f"\t{el}")
        #fin p

        #  Etape 42 : On instancie les pistes mais pas les liaisons de la premiere et de la dernière section
        for section_index in range(len(self._sections)):
            section = self._sections[section_index]
            if "id" in section:
                del section["id"]
            section = Section(env, section_index, margin_min, pod_size, self._is_bridge, **section)
            self._sections[section_index] = section
        for step_index in range(len(self._steps)):
            step = self._steps[step_index]
            if "id" in step:
                del step["id"]
            step["previous"] = self._sections[step_index]
            step["next"] = self._sections[step_index + 1]
            if step["type"] == "sensor":
                step = Sensor(env, step_index, **step)
            elif step["type"] == "shed":
                step = Shed(env, step_index, **step)
            elif step["type"] == "station":
                step = Station(env, step_index, **step)
            #p debut
            elif step["type"] == "HangarSimple":
                step = HangarSimple(env, step_index, **step)
            elif step["type"] == "HangarRevision":
                step = HangarRevision(env, step_index, **step)
            elif step["type"] == "HangarLavage":
                step = HangarLavage(env, step_index, **step)
            #p fin
            else:
                raise TypeError("invalid element type")
            self._steps[step_index] = step

    @property
    def sections(self):
        """Sections au sein de la route"""
        return self._sections

    @property
    def previous(self):
        """Route précédente au sein de la boucle"""
        return self._previous

    @previous.setter
    def previous(self, value):
        self._previous = value

    @property
    def next(self):
        """Route suivante au sein de la boucle"""
        return self._next

    @next.setter
    def next(self, value):
        self._next = value

    @property
    def steps(self):
        """Liste des étapes au sein de la route (gares, capteurs, dépôts)"""
        return self._steps

    @property
    def sensors(self):
        """Liste des capteurs au sein de la route"""
        return [step for step in self._steps if isinstance(step, Sensor)]

    @property
    def sheds(self):
        """Liste des dépôts au sein de la route"""
        return [step for step in self._steps if isinstance(step, Shed)]
    
    #p_tb debut
    @property
    def hangarsSimples(self):
        return [step for step in self._steps if isinstance(step, HangarSimple)]

    @property
    def hangarsRevision(self):
        return [step for step in self._steps if isinstance(step, HangarRevision)]

    @property
    def hangarsLavage(self):
        return [step for step in self._steps if isinstance(step, HangarLavage)]
    #p_tb fin

    @property
    def stations(self):
        """Liste des gares au sein de la route"""
        return [step for step in self._steps if isinstance(step, Station)]

    @property
    def pods(self):
        """Liste des capsules au sein de la route"""
        return [pod for track in self._sections + self._steps for pod in track.pods]

    @property
    def length(self):
        """Taille de la route"""
        length = 0
        for section in self._sections:
            length += section.length
        return length

    @property
    def weight(self):
        """Poids actuel de la route (qui dépend de la congestion), à ne pas confondre avec expected_weight
        à l'initialisation on a weight = expected_weight puis cela évolue avec le traffic"""
        return self._weight

    @weight.setter
    def weight(self, value):
        self._weight = value

    @property
    def expected_weight(self):
        """Poids de la route ne dépendant pas de la congestion"""
        weight = 0
        for section in self._sections:
            weight += section.weight
        return weight

    # Les 4 propriétés suivantes servent au placement des entités dans la vue (c'est lié à la viewBox)

    @property
    def x_min(self):
        return self.min_xy(True)

    @property
    def x_max(self):
        return self.max_xy(True)

    @property
    def y_min(self):
        return self.min_xy(False)

    @property
    def y_max(self):
        return self.max_xy(False)

    @property
    def name(self):
        """Nom de la route"""
        return super().name or "Road %d" % self.id

    def min_xy(self, choice):
        """
        :param choice: si True alors on travaille avec x (abscisse) sinon on travaille en y (ordonnée)
        :return: (float) la plus petite abscisse ou ordonnée selon le choix, parmi les éléments de la route
        (utile pour récupérer les dimensions du réseau dans la vue)
        """
        mini = inf
        for step in self._steps:
            if choice:
                temp = step.x
            else:
                temp = step.y
            if temp < mini:
                mini = temp
        return mini

    def max_xy(self, choice):
        """
        :param choice: si True alors on travaille avec x (abscisse) sinon on travaille en y (ordonnée)
        :return: (float) la plus grande abscisse ou ordonnée selon le choix, parmi les éléments de la route
        (utile pour récupérer les dimensions du réseau dans la vue)
        """
        maxi = 0
        for step in self._steps:
            if choice:
                temp = step.x
            else:
                temp = step.y
            if temp > maxi:
                maxi = temp
        return maxi

    def serialize(self):
        """Sérialise les informations de la route pour les envoyer à la vue"""
        pods = [pod.serialize() for section in self._sections for pod in section.pods]
        dict = super().serialize()
        dict.update({
            "pods": pods
        })
        return dict

    def find(self, step):
        """Permet de trouver une étape dans la route par rapport à la boucle"""
        return self.parent.find(step)

    def init_parent_of_children(self):
        """
        Initialise le parent des pistes de la route comme étant la route
        :return: void
        """
        for section in self._sections:
            section.parent = self
        for step in self._steps:
            step.parent = self

    @property
    def updatable(self):
        return False

    def update(self):
        return

    def handle_message(self, message):
        
        if "pod_entry" == message["type"]:
            # La route prévient la bonne piste / aiguillage qu'une capsule est sortie
            new_track = message["author"]
            pod = message["pod"]
            if isinstance(new_track, Switch):
                track = new_track.previous.sections[-1]
            else:
                track = new_track.previous
            #print(f"{self.name} écrit pod_exit à {track.name}")
            track.write({
                "author": self,
                "type": "pod_exit",
                "pod": pod
            })
        elif "docked" == message["type"]:
            # La route remonte l'information d'un stationnement au réseau
            pod = message["pod"]
            self._parent.write({
                "author": self,
                "type": "docked",
                "pod": pod,
                "timestamp": message["timestamp"]
            })
        elif "refill" == message["type"]:
            station = message["station"]
            self.parent.write({
                "author": self,
                "type": "refill",
                "station": station
            })
        elif "empty" == message["type"]:
            station = message["station"]
            self.parent.write({
                "author": self,
                "type": "empty",
                "station": station
            })
        elif "departure" == message["type"]:
            self.parent.write({
                "author": self,
                "pod": message["pod"],
                "type": "departure",
                "origin": message["author"].name,
                "destination": message["destination"],
                "timestamp": message["timestamp"],
                "waiting_time": message["waiting_time"],
                "traveler": message["traveler"]
            })
        else:
            raise ValueError("Invalid message")

