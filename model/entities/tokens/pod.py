from numpy.random import normal, seed

from .token import Token
from .traveler import Traveler
from ..nodes.networks.ways.tracks.GestionnaireLavage import GestionnaireLavage
from ..nodes.networks.ways.tracks.GestionnaireRevision import GestionnaireRevision

_moving_pods = []
_moving_travelers = 0
_seed_for_pods = 42   # Nécessaire pour que la simulation soit reproductible

class Pod(Token):
    """
    Classe modélisant une capsule du réseau UrbanLoop, elle est autonome et reçoit
    des ordres de vitesses qui peuvent être sur une certaine distance
    au niveau des aiguillages
    """

    quickInfos_nextIndex = 0

    def __init__(self, env, track_or_switch, pod_speed, position=None, travelers=None, speed_restore=None, length_before_restore=None, turn=None, coef=None, acceleration=None, brake=None, during_departure=None, traveled_distance=None, traveled_distance_t=None,
                 nombre_signalements_doit_aller_en_revision=None,
                 dernier_signalement_revision_par_vrai_utilisateur=None,
                 temps_depuis_revision=None,
                 distance_depuis_revision=None,
                 temps_restant_attente_en_revision=None,
                 en_direction_revision=None,
                 nombre_signalements_doit_aller_au_lavage=None,
                 dernier_signalement_lavage_par_vrai_utilisateur=None,
                 temps_restant_attente_au_lavage=None,
                 en_direction_lavage=None,
                 quickInfos_index=None,
                 **kwargs):
        self._speed = pod_speed
        self._end_speed = self._speed # placé avant super().__init__() car on a besoin de _end_speed et _speed pour `self.updatable()`
        super().__init__(env, **kwargs)
        self._position = position or 0
        travelers = travelers or {
            "count": 0,
            "max": 1
        }
        travelers["count"] = travelers["count"] or 0
        travelers["max"] = travelers["max"] or 0
        self._travelers = [Traveler(env, 0) for _ in range(travelers["count"])]
        self._capacity = travelers["max"]
        self._track_or_switch = track_or_switch
        self._source = self.source or None  # si la capsule a déjà été créée mais change de voie, source n'est pas changé, sinon on setup via track_or_switch
        self._destination = self.destination or None
        self._turn = turn or False
        self._length_before_restore = length_before_restore or None
        self._speed_restore = speed_restore or None

        global _seed_for_pods
        seed(_seed_for_pods) # apparemment c'est une mauvaise pratique de redéfinir la seed au milieu de nul part (il est conseillé d'utilisé un autre random generator)
        _seed_for_pods += 1         

        self._coef = normal(1, 0.05/2) # Gaussienne à 95% de confiance (car pour avoir "moy +/- 2*sigma = [0.95,1.05]" il faut sigma = 0.05/2) (et pour 99.7% de confiance : 0.05/3)
        if self._coef > 1.05:
            self._coef = 1.05
            self._failing = True
        elif self._coef < 0.95:
            self._coef = 0.95
            self._failing = True
        else:
            self._failing = False
        self._contain_real_user = False
        self._changed_destination = False
        self._emergency_exit = False
        self._acceleration = acceleration or 2
        self._brake = brake or 5
        self._during_departure = during_departure or False
        self._traveled_distance = traveled_distance or 0
        self._traveled_distance_t = traveled_distance_t or 0
        self._previous_station = None

        #p_tbtc debut
        self._nombre_signalements_doit_aller_en_revision = nombre_signalements_doit_aller_en_revision or GestionnaireRevision.genererNombreSignalementsAleatoire()
        self._dernier_signalement_lavage_par_vrai_utilisateur = dernier_signalement_lavage_par_vrai_utilisateur or False
        self._temps_depuis_revision = temps_depuis_revision or GestionnaireRevision.genererTempsAleatoire()
        self._distance_depuis_revision = distance_depuis_revision or GestionnaireRevision.genererDistanceAleatoire()
        self._temps_restant_attente_en_revision = temps_restant_attente_en_revision or -1
        self._en_direction_revision = en_direction_revision or False

        self._nombre_signalements_doit_aller_au_lavage = nombre_signalements_doit_aller_au_lavage or GestionnaireLavage.genererNombreSignalementsAleatoire()
        self._dernier_signalement_revision_par_vrai_utilisateur = dernier_signalement_revision_par_vrai_utilisateur or False
        self._temps_restant_attente_au_lavage = temps_restant_attente_au_lavage or -1
        self._en_direction_lavage = en_direction_lavage or False

        self._quickInfos_index = quickInfos_index
        if self._quickInfos_index is None:
            self._quickInfos_index = Pod.quickInfos_nextIndex
            Pod.quickInfos_nextIndex += 1
        self._quickInfos = ""
        self.set_quickInfos()

        print(f"Pod créé - quickInfos : {self._quickInfos} - objet : {self}")
        #p_tbtc fin


    @property
    def nombre_signalements_doit_aller_en_revision(self):
        return self._nombre_signalements_doit_aller_en_revision

    @nombre_signalements_doit_aller_en_revision.setter
    def nombre_signalements_doit_aller_en_revision(self, value):
        self._nombre_signalements_doit_aller_en_revision = value

    @property
    def dernier_signalement_revision_par_vrai_utilisateur(self):
        return self._dernier_signalement_revision_par_vrai_utilisateur

    @dernier_signalement_revision_par_vrai_utilisateur.setter
    def dernier_signalement_revision_par_vrai_utilisateur(self, value):
        self._dernier_signalement_revision_par_vrai_utilisateur = value

    @property
    def temps_depuis_revision(self):
        return self._temps_depuis_revision

    @temps_depuis_revision.setter
    def temps_depuis_revision(self, value):
        self._temps_depuis_revision = value

    @property
    def distance_depuis_revision(self):
        return self._distance_depuis_revision

    @distance_depuis_revision.setter
    def distance_depuis_revision(self, value):
        self._distance_depuis_revision = value

    @property
    def temps_restant_attente_en_revision(self):
        return self._temps_restant_attente_en_revision

    @temps_restant_attente_en_revision.setter
    def temps_restant_attente_en_revision(self, value):
        self._temps_restant_attente_en_revision = value

    @property
    def en_direction_revision(self):
        return self._en_direction_revision

    @en_direction_revision.setter
    def en_direction_revision(self, value):
        self._en_direction_revision = value

    @property
    def nombre_signalements_doit_aller_au_lavage(self):
        return self._nombre_signalements_doit_aller_au_lavage

    @nombre_signalements_doit_aller_au_lavage.setter
    def nombre_signalements_doit_aller_au_lavage(self, value):
        self._nombre_signalements_doit_aller_au_lavage = value

    @property
    def dernier_signalement_lavage_par_vrai_utilisateur(self):
        return self._dernier_signalement_lavage_par_vrai_utilisateur

    @dernier_signalement_lavage_par_vrai_utilisateur.setter
    def dernier_signalement_lavage_par_vrai_utilisateur(self, value):
        self._dernier_signalement_lavage_par_vrai_utilisateur = value

    @property
    def temps_restant_attente_au_lavage(self):
        return self._temps_restant_attente_au_lavage

    @temps_restant_attente_au_lavage.setter
    def temps_restant_attente_au_lavage(self, value):
        self._temps_restant_attente_au_lavage = value

    @property
    def en_direction_lavage(self):
        return self._en_direction_lavage

    @en_direction_lavage.setter
    def en_direction_lavage(self, value):
        self._en_direction_lavage = value

    @property
    def quickInfos_index(self):
        return self._quickInfos_index

    def set_quickInfos(self): #p_tbtc
        self._quickInfos = f"Pod {self._quickInfos_index}\n{self.source}->{self.destination}"
        if self._en_direction_lavage:
            self._quickInfos += "\nVers lavage"
        elif self.nombre_signalements_doit_aller_au_lavage:
            self._quickInfos += "\nÀ laver"
        if self._en_direction_revision:
            self._quickInfos += "\nVers révision"
        elif self.nombre_signalements_doit_aller_en_revision:
            self._quickInfos += "\nÀ réviser"

    def demander_envoi_lavage(self, user_id):
        self._nombre_signalements_doit_aller_au_lavage += 1
        print(f"Pod {self._quickInfos_index} est signalé comme étant à laver ({self._nombre_signalements_doit_aller_au_lavage})")

    def demander_envoi_revision(self, user_id):
        self._nombre_signalements_doit_aller_en_revision += 1
        print(f"Pod {self._quickInfos_index} est signalé comme étant à réviser ({self._nombre_signalements_doit_aller_en_revision})")

    @property
    def position(self):
        """
        Position de la capsule depuis le début de la section où elle se trouve
        Si pas sur une section alors ça vaut 0
        Si sur un aiguillage, alors comme il a une taille c'est != 0
        Attention, pour un fichier complet d'un réseau on indique la position depuis le début de la boucle
        """
        return self._position

    @position.setter
    def position(self, value):
        """setter de l'attribut position"""
        self._position = value

    @property
    def travelers(self):
        """Liste des voyageurs dans la capsule"""
        return self._travelers

    @travelers.setter
    def travelers(self, new_travelers):
        """setter de l'attribut travelers"""
        global _moving_travelers
        global _moving_pods
        _moving_travelers += len(new_travelers) - len(self._travelers)
        self._travelers = new_travelers
        if len(self._travelers) == 0 and self in _moving_pods:
            _moving_pods.remove(self)
        if len(self._travelers) > 0 and self not in _moving_pods:
            _moving_pods.append(self)
        # print("\u001B[36m moving travelers =", len(_moving_pods), "\u001B[0m")  # cyan

    def is_empty(self):
        return len(self._travelers) == 0

    @property
    def capacity(self):
        """nombre de voyageurs maximal dans la capsule"""
        return self._capacity

    @property
    def track_or_switch(self):
        """setter de l'attribut track_or_switch"""
        return self._track_or_switch

    @track_or_switch.setter
    def track_or_switch(self, value):
        """piste (section ou étape) ou aiguillage où se trouve la capsule"""
        self._track_or_switch = value
        previousStation = self.get_station_if_on_switch(self._track_or_switch.previous)
        if previousStation != None:
            self._previous_station = previousStation
    
    @property
    def source(self):
        """setter de l'attribut source"""
        return self._source

    @source.setter
    def source(self, value):
        self._source = value

    @property
    def destination(self):
        """setter de l'attribut destination"""
        return self._destination

    @destination.setter
    def destination(self, value):
        self._destination = value

    @property
    def name(self):
        """nom de la capsule"""
        return super().name or "Pod %s" % self.id

    @property
    def speed(self):
        """vitesse actuel de la capsule"""
        return self._speed

    @speed.setter
    def speed(self, value):
        """setter de l'attribut speed"""
        self._end_speed = value * self._coef

    @property
    def speed_restore(self):
        """
        vitesse à restaurer après avoir parcouru la distance length_before_restore
        lors d'un ordre de vitesse sur une certaine distance
        """
        return self._speed_restore

    @property
    def length_before_restore(self):
        """
        distance à parcourir avant de retrouver la vitesse speed_restore
        lors d'un ordre de vitesse sur une certaine distance
        """
        return self._length_before_restore

    @property
    def failing(self):
        """
        Renvoie si la capsule est défaillante ou non
        """
        return self._failing
    
    @property
    def turn(self):
        """si la station est sur un SwitchOut, indique si elle est autorisée à entrer sur le bridge"""
        return self._turn

    @property
    def during_departure(self):
        """si le pod a déjà reçu l'ordre de quitter sa station"""
        return self._during_departure
        
    @during_departure.setter
    def during_departure(self, value):
        self._during_departure = value

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "name": self.name,
            "position": self.position,
            "travelers": {
                "count": len(self.travelers),
                "max": self.capacity
            },
            "speed_restore": self.speed_restore,
            "length_before_restore": self.length_before_restore,
            "speed": self.speed,
            "source": self.source,
            "destination": self.destination,
            "failing": self.failing,
            "contain_real_user": self._contain_real_user,
            "changed_destination": self._changed_destination,
            "emergency_exit": self._emergency_exit,
            "coef": self._coef,
            "acceleration": self._acceleration,
            "brake": self._brake,
            "during_departure": self._during_departure,
            "traveled_distance": self._traveled_distance,
            "traveled_distance_t": self._traveled_distance_t,
            #p_tbtc debut
            "nombre_signalements_doit_aller_en_revision": self._nombre_signalements_doit_aller_en_revision,
            "dernier_signalement_revision_par_vrai_utilisateur": self._dernier_signalement_revision_par_vrai_utilisateur,
            "distance_depuis_revision": self._distance_depuis_revision,
            "temps_depuis_revision": self._temps_depuis_revision,
            "temps_restant_attente_en_revision": self._temps_restant_attente_en_revision,
            "dernier_signalement_lavage_par_vrai_utilisateur": self._dernier_signalement_lavage_par_vrai_utilisateur,
            "en_direction_revision": self._en_direction_revision,
            "nombre_signalements_doit_aller_au_lavage": self._nombre_signalements_doit_aller_au_lavage,
            "temps_restant_attente_au_lavage": self._temps_restant_attente_au_lavage,
            "en_direction_lavage": self._en_direction_lavage,
            "quickInfos_index": self._quickInfos_index,
            "quickInfos": self._quickInfos
            #p_tbtc fin
        })
        return dict

    def closest(self):
        return self._track_or_switch.closest(self)

    @property
    def updatable(self):
        return self._end_speed != 0 and self._speed != 0

    def activate_updates(self):
        if self._env.with_messages == False and self not in self._env.updatable_entities:
            self._env.updatable_entities.append(self)

    def deactivate_updates(self):
        if self._env.with_messages == False and self in self._env.updatable_entities:
            self._env.updatable_entities.remove(self)

    def update(self):

        #p_tbtc debut
        self._temps_depuis_revision += self.env.tick
        self.set_quickInfos()
        #p_tbtc fin

        # OPTIMISATION : ne pas regarder à chaque update ?
        self._contain_real_user = False
        for traveler in self._travelers:       
            # On regarde si un de nos passagers a été genéré avec un ticket via l'appli mobile
            self._contain_real_user = traveler.real_user   
            self._changed_destination = traveler.changed_dest   
            self._emergency_exit = traveler.called_emergency_exit   

        # Gestion du décalage et de la discrétisation : on reprend la vitesse moyenne après avoir parcouru la bonne distance
        if self._length_before_restore is not None:
            if self._length_before_restore > 0:
                self._length_before_restore -= self._speed * self.env.tick
            else:
                self._length_before_restore = None
                if self._speed_restore is not None:
                    self.speed = self._speed_restore
                    self._speed_restore = None

        # La capsule accélère ou freine
        if self._speed < self._end_speed:
            self._speed += self._acceleration
            if self._speed > self._end_speed:
                self._speed = self._end_speed
        elif self._speed > self._end_speed:
            self._speed -= self._brake
            if self._speed < self._end_speed:
                self._speed = self._end_speed

        # La capsule détecte la capsule la plus proche devant elle
        if type(self._track_or_switch).__name__ == "Section":
            closest, same_section = self.closest()
            if closest:
                if same_section:
                    diff = closest.position - self._position
                else:
                    diff = closest.position + (self._track_or_switch.length - self._position)
                if diff < self._track_or_switch.margin:
                    self.speed = closest.speed / 2
                # Si la plus proche est trop loin on réaugmente la vitesse
                elif self._speed < self._track_or_switch.speed:
                    self.speed = self._track_or_switch.speed
            # S'il n'y a pas de capsule devant on réaugmente la vitesse
            elif self._speed < self._track_or_switch.speed:
                self.speed = self._track_or_switch.speed
                #
                # ^ TODO : utiliser l'accélération
        
        # La capsule avance
        if self._speed != 0:
            self._position += self._speed * self.env.tick
            self._traveled_distance += self._speed * self.env.tick
            if len(self._travelers) > 0:
                self._traveled_distance_t += self._speed * self.env.tick

        # La capsule s'insère sur un bridge si elle en a reçu l'ordre
        if self._position > self._track_or_switch.length and type(self._track_or_switch).__name__ == "SwitchOut" and self._turn:
            self.position -= self._track_or_switch.length
            new_section = self._track_or_switch.beside.sections[0]
            self.track_or_switch = new_section

            if self.position > new_section.length:
                print("Warning: pod.py: a pod has travelled to much distance in a same tick while entering a bridge.")
            self._track_or_switch.write({
                "author": self,
                "type": "pod_entry",
                "pod": self
            })
            self._turn = False

        # La capsule arrive sur une nouvelle piste / aiguillage
        elif self._position > self._track_or_switch.length:
            bridge_to_switch = False
            self._position -= self._track_or_switch.length
            t = self._position / self._speed

            # si on quitte un switch
            if type(self._track_or_switch).__name__ in ["SwitchOut", "SwitchIn"]:
                self.track_or_switch = self._track_or_switch.next.sections[0]

            # si on quitte une section
            else:
                if type(self._track_or_switch).__name__ == "Section":
                    next_elem = self._track_or_switch.next
                    if self._track_or_switch.is_bridge and type(next_elem).__name__ == "SwitchIn":
                                                           # ça ne fonctionnera pas si on a un bridge dans un bridge
                                                           # TODO : vérifier la structure du réseau pour ne pas avoir de bridge dans un bridge ?
                        # la capsule entre sur une route depuis un pont
                        bridge_to_switch = True
                    self._track_or_switch = next_elem
                else:
                    # si on quitte une step (shed, station, sensor)
                    self.track_or_switch = self._track_or_switch.next
                    pass

            self._position = t * self._track_or_switch.speed
            if bridge_to_switch:
                self._track_or_switch.write({
                    "author": self,
                    "type": "pod_entry_from_bridge",
                    "pod": self
                })
            else:
                if type(self._track_or_switch).__name__ in ["Station", "Shed"]:
                    self._position = 0
                self._track_or_switch.write({
                    "author": self,
                    "type": "pod_entry",
                    "pod": self
                })
            # on vérifie si le pod n'est pas allé trop loin
            #if self._position > self._track_or_switch.length and type(self._track_or_switch).__name__ not in ["SwitchOut", "Shed", "Station", "Sensor"]:
            if self._position > self._track_or_switch.length and type(self._track_or_switch).__name__ not in [
                    "SwitchOut", "Shed", "Station", "Sensor", "HangarSimple", "HangarRevision", "HangarLavage"]:
                print("Warning: pod.py: a pod has travelled to much distance while arriving on '%s'." % self._track_or_switch.name)
        
        return
    
    def handle_message(self, message):
        # Gestion des messages reçus
        
        if "speed" == message["type"]:
            # Ordre de changement de vitesse
            self.speed = message["speed"]

        elif "passing" == message["type"]:
            # C'était en partie utilisé lorsque des stations/sheds étaient directement sur les boucles.
            # Maintenant, on a toujours besoin de ce cas pour les Sensors.
            self.track_or_switch = self._track_or_switch.next
            self._track_or_switch.write({
                "author": self,
                "type": "pod_entry",
                "pod": self,
                "traveled_distance": self._traveled_distance
            })
            
        elif "passing_from_switch" == message["type"]:
            self._track_or_switch = self._track_or_switch.next.sections[0]
            self._track_or_switch.write({
                "author": self,
                "type": "pod_entry",
                "pod": self,
                "traveled_distance": self._traveled_distance
            })
            
        elif "docked" == message["type"]:
            # La capsule s'arrête dans une gare ou un dépôt
            self._speed = 0
            self._end_speed = 0
            self._previous_station = None      # On reset la derniere station
            self.deactivate_updates()
        
        elif "insert" == message["type"]:
            # Ordre d'insertion, la capsule est autorisée à tourner
            self._turn = True
                
        elif "speed_a_while" == message["type"]:
            # Ordre de vitesse lors d'un décalage pour laisser une capsule s'insérer
            # Ou lors d'une discrétisation
            # La capsule prend une vitesse sur une certaine distance puis reprend la vitesse moyenne
            self.speed = message["speed"]
            self._length_before_restore = message["length_before_restore"]
            self._speed_restore = message["speed_restore"]
        elif "departure" == message["type"]:
            # La capsule part d'un dépôt ou d'une gare
            self._source = message["author"].name
            self._destination = message["destination"]
            #print(f"pod {str(self)} : self._track_or_switch est {self._track_or_switch.name}")
            self._track_or_switch = self._track_or_switch.next
            #print(f"self._track_or_switch passe à {self._track_or_switch.name}")
            self._endSpeed = self._track_or_switch.speed
            self.activate_updates()
            self._track_or_switch.write({
                "author": self,
                "type": "pod_entry",
                "pod": self,
                "traveled_distance": self._traveled_distance
            })
        else:
            raise ValueError("Invalid message: ", message)

    def get_previous_station(self):   # Pas de table de routage pr celui-ci
        """ Donne la prochaine station traversee par la capsule """ 

        if (self._previous_station == None):
            self._previous_station = self.source
        return self._previous_station


    def get_next_station(self): 
        """ Donne la prochaine station traversee par la capsule """ 
        eltOfNetwork = self._track_or_switch

        nbIter = 0              # Pour eviter une boucle infinie
        nextStation = None

        while (nextStation is None and nbIter < 200):   
            while (type(eltOfNetwork).__name__ != "SwitchOut"):     # On cherche le SwitchOut le plus proche
                if ((type(eltOfNetwork).__name__ == "Road") and (len(eltOfNetwork.stations) > 0)):  # Route contenant la station
                    return self.get_stations_of_road(eltOfNetwork)
                eltOfNetwork = eltOfNetwork.next
            nextStation = self.get_station_on_bridge_derivation(eltOfNetwork)
            if (nextStation is None): # On a pas reussi a trouver une mini boucle assez proche, on va devoir regarder les tables de routage du SwitchOut
                if (eltOfNetwork._is_route(self)):      # On regarde le beside (cad qu'on prend le pont (les pointilles) au SwitchOn)
                    eltOfNetwork = eltOfNetwork.beside
                else:                                   # sinon on regarde le trajet normal du switch
                    eltOfNetwork = eltOfNetwork.next
            nbIter += 1
        return nextStation


    def get_time_before_arrival(self):
        """Renvoie la duree avant arrivee a destination"""

        eltOfNetwork = self._track_or_switch


        # On regarde si on ne se trouve pas sur la derivation finale
        if (type(eltOfNetwork.previous).__name__ == "SwitchOut" and self.get_station_on_bridge_derivation(eltOfNetwork.previous) == self._destination):
            return " Time = " + str(self.get_time_of_elt_of_network(eltOfNetwork))

        nbIter = 0  # Pour eviter une boucle infinie
        stationConsidered = None
        timeToDest = (eltOfNetwork.length - self._position) / self._track_or_switch.speed
        # Pas de problemes pour chercher la speed, car self._track_or_switch ne peut etre une road (j'ai l'impression)

        while ( (stationConsidered != self._destination) and (nbIter < 200) ):   
            while (type(eltOfNetwork).__name__ != "SwitchOut"):     # On cherche le SwitchOut le plus proche
                if ((type(eltOfNetwork).__name__ == "Road") and (len(eltOfNetwork.stations) > 0)):  # Route contenant la station
                    timeToDest += self.get_time_of_elt_of_network(eltOfNetwork.next)

                    for station in eltOfNetwork.stations:
                        stationConsidered = station.name        
                        break  # On recupere juste la premiere station (on ne considere pas le cas ou il y en a plusieurs)
                    
                    # A ce stade-la, stationConsidered == self._destination
                    # En effet, une capsule ne peut (et ne doit) pas aller ds une mini-boucle ne menant pas a sa destination

                    break       # On ne va pas continuer a chercher un SwitchOut, car on est arrive a la destination (a la route pres)

                timeToDest += self.get_time_of_elt_of_network(eltOfNetwork.next)
                eltOfNetwork = eltOfNetwork.next

            if (stationConsidered == self._destination):  # Dans le cas on l'on a trouve grace au "for station"
                break

            # On cherche la station mtn qu'on est a un switchOut, ou le prochain switchOut
            stationConsidered = self.get_station_on_bridge_derivation(eltOfNetwork)
            if (stationConsidered is None):  # On n'a pas reussi a trouver une mini boucle assez proche, on va devoir regarder les tables de routage du SwitchOut
                if (eltOfNetwork._is_route(self)):      # On regarde le beside (cad qu'on prend le pont (les pointilles) au SwitchOn)
                    timeToDest += self.get_time_of_elt_of_network(eltOfNetwork.beside)
                    eltOfNetwork = eltOfNetwork.beside
                else:                                   # sinon on regarde le trajet normal du switch
                    timeToDest += self.get_time_of_elt_of_network(eltOfNetwork.next)
                    eltOfNetwork = eltOfNetwork.next
            elif (stationConsidered != self._destination):    # On a trouve une mini boucle, mais pas avec la station destination
                timeToDest += self.get_time_of_elt_of_network(eltOfNetwork.next)
                eltOfNetwork = eltOfNetwork.next    # On passe notre chemin
                
            nbIter += 1


        timeInsideBridgeDerivationOfArrival = self.get_time_of_elt_of_network(eltOfNetwork)
        timeToDest += timeInsideBridgeDerivationOfArrival

        # A FAIRE POUR TRISTAN
        # Actuellement, on ne considere pas le temps de parcours d'un bridge-derivation contenant la station destination")
        # Faire que get_station_on_bridge_derivation renvoient en plus un temps pour faire cela

        # (considere juste la vitesse de la section/switch ou la capsule se trouve, mais pas sa vitesse actuelle/vitesse future reelle en fction du traffic)
        return " Time = " + str(timeToDest) + " (surement faux quand traffic)"


    def get_time_of_elt_of_network(self, eltOfNetwork):
        """ Renvoie la duree necessaire pr parcourir un element du reseau, ou le pod ne se trouve pas """
        timeOfElt = 0

        if (type(eltOfNetwork).__name__ == "Road"):     # Road n'a pas d'attribut speed, mais possede des sections
            # par contre j'ai l'impression qu'il y a toujours qu'une seule section par road ...
            for section in eltOfNetwork.sections:
                timeOfElt += (section.length / section.speed)
        else:
            timeOfElt = eltOfNetwork.length / eltOfNetwork.speed
        return timeOfElt


    # Deprecated
    def get_station_on_mini_loop(self, eltOfNetwork):
        """ Renvoie le nom de la station sur la mini-boucle actuelle, en partant d'un Switch """
        if (type(eltOfNetwork).__name__ == "SwitchOut"):
            return self.get_stations_of_road(eltOfNetwork.beside.next.next)
        elif (type(eltOfNetwork).__name__ == "SwitchIn"):
            return self.get_stations_of_road(eltOfNetwork.beside.previous.previous)
        else :
            return None

    def get_station_of_road(self, aRoad):
        """ Renvoie le nom de la station (qu'une seule normalement) sur la road """
        if (type(aRoad).__name__ == "Road"):
            if (len(aRoad.stations) > 0):      
                for station in aRoad.stations:
                    return station.name  # On renvoie direct car on considere qu'il n'y a qu'une station au max par road (potentiellement a changer plus tard)
            return None


    def get_station_if_on_switch(self, eltOfNetwork):
        if (type(eltOfNetwork).__name__ == "SwitchOut" or type(eltOfNetwork).__name__ == "SwitchIn"):
            return self.get_station_on_bridge_derivation(eltOfNetwork)
        else :
            return None

    def get_station_on_bridge_derivation(self, eltOfNetwork):
        """ Renvoie le nom de la station sur la bridge-derivation actuelle, en partant d'un Switch """
        steps = eltOfNetwork.beside.steps
        if (len(steps) == 0):
            return None
        if (type(steps[0]).__name__ == "Station"):
            return steps[0].name
        else :
            return None

    def change_destination(self, user_id, new_dest):
        self._destination = new_dest
        has_found_traveler = False
        for a_traveler in self._travelers:
            if (a_traveler.id == str(user_id)):
                a_traveler.change_destination()
                has_found_traveler = True
        if (has_found_traveler == False):
            print("Error in change_destination")

    def call_emergency_exit(self, user_id):
        self._destination = self.get_next_station()
        for a_traveler in self._travelers:
            if (a_traveler.id == str(user_id)):
                a_traveler.call_emergency_exit()
                has_found_traveler = True
        if (has_found_traveler == False):
            print("Error in call_emergency_exit")
