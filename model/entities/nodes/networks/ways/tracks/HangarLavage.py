from .Hangar import Hangar


class HangarLavage(Hangar):
    """ Classe modélisant un hangar de lavage=dépôt de lavage"""
    def __init__(self, env, id, departure_pods=None, pods=None, element_of_loop=None,
                 enLavage=None,
                 **kwargs):
        super().__init__(env, id, departure_pods, pods, element_of_loop, **kwargs)
        #p_tbtc
        print("Hangar lavage créé")
        self._enLavage = enLavage or []

    def serialize(self):
        """sérialise les informations du dépôt"""
        dico = super().serialize()
        enLavage = [{"pod": pod.serialize()} for pod in self._enLavage]
        dico.update({
            "type": f"{self.__class__.__name__}",
            "enLavage": enLavage
        })
        return dico

    @property
    def temps_lavage(self):
        return self.parent.parent.gestionnaireLavage.temps_lavage

    def ajouterEnLavage(self, pod):
        if pod not in self._enLavage:
            self._enLavage.append(pod)

    def retirerEnLavage(self, pod):
        if pod in self._enLavage:
            self._enLavage.append(pod)

    def update(self):
        """Fonction gérant le processus dépôt"""

        # Attente pour le prochain départ
        if self._wait != -1:
            self._wait += self.env.tick
            if self._wait > self.next.margin / self.next.speed:
                self._wait = -1

        #p_tbtc MAJ des temps de révision
        for pod in self._enLavage:
            pod.temps_restant_attente_en_lavage -= 1
            #print(f"{pod} : compteur de révision a décru de 1 : {pod.temps_restant_attente_en_lavage}")
            if pod.temps_restant_attente_en_lavage == 0:
                print(f"Pod {pod.quickInfos_index} : lavage terminé")
                pod.nombre_signalements_doit_aller_au_lavage = 0
                pod.temps_restant_attente_au_lavage = -1
                self._departure_pods.append(pod)
                self._enLavage.remove(pod)

        # Départ des capsules #p_tbtc
        if self._departure_pods and self._wait == -1:
            self._wait = 0
            road = self.parent
            nw = road.parent
            #pod = self._departure_pods[0]
            pod = self._departure_pods.pop(0)
            if pod not in self._enLavage:
                if self.gestionnaireRevision.podDoitAllerEnRevision(pod):
                    pod.en_direction_revision = True
                    destination = nw.gestionnaireRevision.obtenirDestination(
                        nom_station_source=self.name,
                        categorie_destination="HangarRevision"
                    )
                else:
                    destination = nw.gestionnaireLavage.obtenirDestination(
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
                print(f"En sortie de lavage, Pod {pod.quickInfos_index} est redirigé vers {destination}")
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
                raise Exception(f"Pod {pod.quickInfos_index} extrait de HangarLavage._departure_pods est encore dans HangarLavage._enLavage")

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
                print(f"Pod {pod.quickInfos_index} entre en hangar de lavage")
                print(f"Son track_or_switch est {pod.track_or_switch.name}")
                #p_tbtc debut
                pod.en_direction_lavage = False
                self._enLavage.append(pod)
                pod.temps_restant_attente_en_lavage = self.temps_lavage
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
                print(f"Pod {pod.quickInfos_index} passe devant un hangar de lavage")
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
            station = message["station"]
            if len(self._pods) > 0 and len(self._pods) > len(self._departure_pods) + len(
                    self.pods_during_departure):  # on vérifie qu'il y a des pods et qu'il ne s'agit pas de pods déjà affectés à une station
                i = 0
                while i < len(self._pods) - 1 and (
                        self._pods[i] in self._departure_pods or self._pods[i].during_departure):
                    i += 1
                pod = self._pods[i]
                pod.destination = station
                self._departure_pods.append(pod)
                print(f"Entrée de Pod {pod.quickInfos_index} en lavage")
            else:
                # on cherche la station concernée,
                # et on l'informe qu'elle ne recevra pas le pod.
                network = self.parent.parent
                found_station = network.get_station_by_name(station)
                found_station.down_incoming_pods()

        else:
            raise ValueError("Invalid message")
