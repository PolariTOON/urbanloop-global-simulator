from random import randint

from .GestionnaireRevision import GestionnaireRevision
from .Hangar import Hangar


class HangarRevision(Hangar):
    """ Classe modélisant un hangar de révision=dépôt de révision"""
    def __init__(self, env, id, departure_pods=None, pods=None, element_of_loop=None, **kwargs):
        super().__init__(env, id, departure_pods, pods, element_of_loop, **kwargs)
        #p_tbtc
        print("Hangar révision créé")
        self._enRevision = [] # TODO à changer pour sérialisation

    def serialize(self):
        """sérialise les informations du dépôt"""
        dico = super().serialize()
        enRevision = [{"pod": pod.serialize()} for pod in self._enRevision]
        dico.update({
            "type": f"{self.__class__.__name__}",
            "enRevision": enRevision
        })
        return dico

    @property
    def temps_revision(self):
        return self.parent.parent.gestionnaireRevision.temps_revision

    @property
    def enRevision(self):
        return self._enRevision

    def ajouterEnRevision(self, pod):
        self._enRevision.append(pod)

    def update(self):
        """Fonction gérant le processus dépôt"""

        # Attente pour le prochain départ
        if self._wait != -1:
            self._wait += self.env.tick
            if self._wait > self.next.margin / self.next.speed:
                self._wait = -1

        #p_tbtc MAJ des temps de révision
        for pod in self._enRevision:
            pod.temps_restant_attente_en_revision -= 1
            #print(f"{pod} : compteur de révision a décru de 1 : {pod.temps_restant_attente_en_revision}")
            if pod.temps_restant_attente_en_revision == 0:
                print(f"Pod {pod.quickInfos_index} : revision terminée")
                pod.nombre_signalements_doit_aller_en_revision = 0
                pod.temps_depuis_revision = 0
                pod.distance_depuis_revision = 0
                pod.temps_restant_attente_en_revision = -1
                self._enRevision.remove(pod)
                self._departure_pods.append(pod)

        # Départ des capsules #p_tbtc
        if self._departure_pods and self._wait == -1:
            self._wait = 0
            road = self.parent
            nw = road.parent
            #pod = self._departure_pods[0]
            pod = self._departure_pods.pop(0)
            if pod not in self._enRevision:
                if self.gestionnaireLavage.podDoitAllerAuLavage(pod):
                    pod.en_direction_lavage = True
                    destination = nw.gestionnaireRevision.obtenirDestination(
                        nom_station_source=self.name,
                        categorie_destination="HangarLavage"
                    )
                else:
                    destination = nw.gestionnaireRevision.obtenirDestination(
                        nom_station_source=self.name,
                        categorie_destination="HangarSimple"
                    )
                pod.during_departure = True
                #print(f"En sortie de révision, {self.name} écrit à {pod} departure vers {destination}")
                pod.write({
                    "author": self,
                    "type": "departure",
                    "destination": destination
                })
                print(f"En sortie de révision, Pod {pod.quickInfos_index} est redirigé vers {destination}")
                # prévient le parent
                #print(f"En sortie de révision, {self.name} écrit à {self.parent.name} departure vers {destination}")
                #print(f"En sortie de révision, {pod} : track_or_switch est {pod.track_or_switch.name}")
                self.parent.write({
                    "author": self,
                    "pod": pod,
                    "type": "departure",
                    "destination": destination,
                    "timestamp": self.env.time,
                    "waiting_time": 0,
                    "traveler": False
                })
            else:
                raise Exception(f"Pod {pod.quickInfos_index} extrait de HangarRevision._departure_pods est encore dans HangarRevision._enRevision")

    def handle_message(self, message):
        if "pod_entry" == message["type"]:
            pod = message["pod"]
            self._parent.write({
                "author": self,
                "type": "pod_entry",
                "pod": pod
            })
            if pod.destination == self.name:
                self._pods.append(pod)
                print(f"Pod {pod.quickInfos_index} entre en hangar de révision")
                print(f"Son track_or_switch est {pod.track_or_switch.name}")
                #p_tbtc debut
                pod.en_direction_revision = False
                self._enRevision.append(pod)
                pod.temps_restant_attente_en_revision = self.temps_revision
                #p_tbtc fin
                pod.write({
                    "author": self,
                    "type": "docked"
                })
                self.parent.write({
                    "author": self,
                    "type": "docked",
                    "pod": pod,
                    "timestamp": self.env.time
                })
            else:
                print(f"Pod {pod.quickInfos_index} passe devant un hangar de révision")
                pod.write({
                    "author": self,
                    "type": "passing"
                })
        elif "pod_exit" == message["type"]:
            pod = message["pod"]
            if pod in self._pods:
                self._pods.remove(pod)
                pod.during_departure = False
            else:
                # dans ce cas, le pod n'était pas docked dans le shed,
                # et on accepte qu'il passe à travers.
                pass
        elif "refill" == message["type"]:
            # Type de message pas encore utilisé
            raise ValueError(f"{self.__class__.__name__} : message refill reçu alors qu'il n'est pas encore utilisé")

        else:
            raise ValueError("Invalid message")
