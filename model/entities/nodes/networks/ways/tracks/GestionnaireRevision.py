# Un gestionnaire par réseau, donc par simulation
# Il faut donc une classe instanciable
# Comme elle fait partie du réseau, nous choisissons de la mettre dans Network
from random import randint
from .Gestionnaire import Gestionnaire


class GestionnaireRevision(Gestionnaire):
    LIMITE_DISTANCE_PARCOURUE_AVANT_REVISION_DEFAUT = 2000
    LIMITE_TEMPS_ECOULE_AVANT_REVISION_DEFAUT = 2000
    TEMPS_REVISION_DEFAUT = 100
    LIMITE_NOMBRE_SIGNALEMENTS_AVANT_REVISION_DEFAUT = 2

    @classmethod
    def genererNombreSignalementsAleatoire(cls):
        if randint(0, 1):
            return randint(0, cls.LIMITE_NOMBRE_SIGNALEMENTS_AVANT_REVISION_DEFAUT-1)
        return randint(0, cls.LIMITE_NOMBRE_SIGNALEMENTS_AVANT_REVISION_DEFAUT-1)
        #return 0

    @classmethod
    def genererDistanceAleatoire(cls):
        return randint(0, cls.LIMITE_DISTANCE_PARCOURUE_AVANT_REVISION_DEFAUT//10)

    @classmethod
    def genererTempsAleatoire(cls):
        return randint(0, cls.LIMITE_TEMPS_ECOULE_AVANT_REVISION_DEFAUT//10)

    @property
    def temps_revision(self):
        return self._temps_revision

    def __init__(
            self,
            network,
            limite_distance_parcourue_avant_revision=None,
            limite_temps_ecoule_avant_revision=None,
            temps_revision=None,
            limite_nombre_signalements_avant_revision=None,
    ):
        super().__init__(network)
        #self._network = network
        self._limite_distance_parcourue_avant_revision = limite_distance_parcourue_avant_revision or GestionnaireRevision.LIMITE_DISTANCE_PARCOURUE_AVANT_REVISION_DEFAUT
        self._limite_temps_ecoule_avant_revision = limite_temps_ecoule_avant_revision or GestionnaireRevision.LIMITE_TEMPS_ECOULE_AVANT_REVISION_DEFAUT
        self._temps_revision = temps_revision or GestionnaireRevision.TEMPS_REVISION_DEFAUT
        self._limite_nombre_signalements_avant_revision = limite_nombre_signalements_avant_revision or GestionnaireRevision.LIMITE_NOMBRE_SIGNALEMENTS_AVANT_REVISION_DEFAUT

        self._liste_pods = self._network.pods

        # self._dict_revision_plus_proche = dict()
        # self._dict_lavage_plus_proche = dict()
        # self._dict_simple_plus_proche = dict()

    def serialize(self):
        return {
            "limite_nombre_signalements_avant_revision": self._limite_nombre_signalements_avant_revision,
            "limite_distance_parcourue_avant_revision": self._limite_distance_parcourue_avant_revision,
            "limite_temps_ecoule_avant_revision": self._limite_temps_ecoule_avant_revision,
            "temps_revision": self._temps_revision
        }

    # def obtenirDestination(self, station_source, categorie_destination="HangarRevision"):
    #     from ...network import shortest_way_tracks
    #
    #     def longueur_chemin(chemin):
    #         longueur_totale = 0
    #         for i in range(len(chemin) - 1):
    #             if chemin[i + 1] is chemin[i].next:
    #                 longueur_totale += chemin[i].next.weight
    #             else:
    #                 longueur_totale += chemin[i].beside.weight
    #         return longueur_totale
    #
    #     if categorie_destination == "HangarRevision":
    #         liste_hangars_possibles = self._network.hangarsRevision
    #         dict_hangars_plus_proches = self._dict_revision_plus_proche
    #     elif categorie_destination == "HangarLavage":
    #         liste_hangars_possibles = self._network.hangarsLavage
    #         dict_hangars_plus_proches = self._dict_lavage_plus_proche
    #     elif categorie_destination == "HangarSimple":
    #         liste_hangars_possibles = self._network.hangarsSimples
    #         dict_hangars_plus_proches = self._dict_simple_plus_proche
    #     else:
    #         raise ValueError(f"Catégorie {categorie_destination} non traitée dans obtenirDestinationDepuisHangarSimple de GestionnaireRevision")
    #
    #     if station_source not in dict_hangars_plus_proches:
    #
    #         if len(liste_hangars_possibles) > 1:
    #             hangar_plus_proche = liste_hangars_possibles[0]
    #             chemin = shortest_way_tracks(station_source, liste_hangars_possibles[0])
    #             longueur_chemin_plus_court = longueur_chemin(chemin)
    #             for i in range(1, len(liste_hangars_possibles)):
    #                 hangar_revision_possible = liste_hangars_possibles[i]
    #                 chemin = shortest_way_tracks(station_source, hangar_revision_possible)
    #                 longueur = longueur_chemin(chemin)
    #                 if longueur < longueur_chemin_plus_court:
    #                     hangar_plus_proche = hangar_revision_possible
    #                     longueur_chemin_plus_court = longueur
    #
    #             dict_hangars_plus_proches[station_source] = hangar_plus_proche
    #
    #         else:
    #             dict_hangars_plus_proches[station_source] = liste_hangars_possibles[0]
    #
    #     return dict_hangars_plus_proches[station_source].name

    # def obtenirDestinationDepuisHangarSimple(self, categorie_destination="HangarRevision"):
    #     # nom_station_source pourrait être ustilisé dans une recherche plus élaborée
    #     if categorie_destination == "HangarRevision":
    #         destination = self._network.hangarsRevision[randint(0, len(self._network.hangarsRevision) - 1)].name
    #     elif categorie_destination == "HangarLavage":
    #         destination = self._network.hangarsLavage[randint(0, len(self._network.hangarsLavage) - 1)].name
    #     else:
    #         raise ValueError(f"Catégorie {categorie_destination} non traitée dans obtenirDestinationDepuisHangarSimple de GestionnaireRevision")
    #     return destination

    def podDoitAllerEnRevision(self, pod):
        return \
                pod.distance_depuis_revision >= self._limite_distance_parcourue_avant_revision \
                or pod.temps_depuis_revision >= self._limite_temps_ecoule_avant_revision \
                or pod.nombre_signalements_doit_aller_en_revision >= self._limite_nombre_signalements_avant_revision \
                or pod.dernier_signalement_revision_par_vrai_utilisateur
