# Un gestionnaire par réseau, donc par simulation
# Il faut donc une classe instanciable
# Comme elle fait partie du réseau, nous choisissons de la mettre dans Network
from random import randint


class GestionnaireRevision:
    LIMITE_DISTANCE_PARCOURUE_AVANT_REVISION_DEFAUT = 2000
    LIMITE_TEMPS_ECOULE_AVANT_REVISION_DEFAUT = 2000
    TEMPS_REVISION_DEFAUT = 100
    LIMITE_NOMBRE_SIGNALEMENTS_AVANT_REVISION_DEFAUT = 2

    @classmethod
    def genererNombreSignalementsAleatoire(cls):
        #if randint(0, 1):
        #    return randint(0, cls.LIMITE_NOMBRE_SIGNALEMENTS_AVANT_REVISION_DEFAUT-1)
        #return randint(cls.LIMITE_NOMBRE_SIGNALEMENTS_AVANT_REVISION_DEFAUT-1, cls.LIMITE_NOMBRE_SIGNALEMENTS_AVANT_REVISION_DEFAUT+2)
        return 0

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
        self._network = network
        self._limite_distance_parcourue_avant_revision = limite_distance_parcourue_avant_revision or GestionnaireRevision.LIMITE_DISTANCE_PARCOURUE_AVANT_REVISION_DEFAUT
        self._limite_temps_ecoule_avant_revision = limite_temps_ecoule_avant_revision or GestionnaireRevision.LIMITE_TEMPS_ECOULE_AVANT_REVISION_DEFAUT
        self._temps_revision = temps_revision or GestionnaireRevision.TEMPS_REVISION_DEFAUT
        self._limite_nombre_signalements_avant_revision = limite_nombre_signalements_avant_revision or GestionnaireRevision.LIMITE_NOMBRE_SIGNALEMENTS_AVANT_REVISION_DEFAUT

        self._liste_pods = self._network.pods

    def serialize(self):
        return {
            "limite_nombre_signalements_avant_revision": self._limite_nombre_signalements_avant_revision,
            "limite_distance_parcourue_avant_revision": self._limite_distance_parcourue_avant_revision,
            "limite_temps_ecoule_avant_revision": self._limite_temps_ecoule_avant_revision,
            "temps_revision": self._temps_revision
        }

    def obtenirDestination(self, nom_station_source, categorie_destination="HangarRevision"):
        # nom_station_source pourrait être ustilisé dans une recherche plus élaborée
        if categorie_destination == "HangarRevision":
            destination = self._network.hangarsRevision[randint(0, len(self._network.hangarsRevision) - 1)].name
        elif categorie_destination == "HangarLavage":
            destination = self._network.hangarsLavage[randint(0, len(self._network.hangarsLavage) - 1)].name
        elif categorie_destination == "HangarSimple":
            destination = self._network.hangarsSimples[randint(0, len(self._network.hangarsSimples) - 1)].name
        else:
            raise ValueError(f"Catégorie {categorie_destination} non traitée dans obtenirDestinationDepuisHangarSimple de GestionnaireRevision")
        return destination

    def obtenirDestinationDepuisHangarSimple(self, categorie_destination="HangarRevision"):
        # nom_station_source pourrait être ustilisé dans une recherche plus élaborée
        if categorie_destination == "HangarRevision":
            destination = self._network.hangarsRevision[randint(0, len(self._network.hangarsRevision) - 1)].name
        elif categorie_destination == "HangarLavage":
            destination = self._network.hangarsLavage[randint(0, len(self._network.hangarsLavage) - 1)].name
        else:
            raise ValueError(f"Catégorie {categorie_destination} non traitée dans obtenirDestinationDepuisHangarSimple de GestionnaireRevision")
        return destination

    def podDoitAllerEnRevision(self, pod):
        return \
                pod.distance_depuis_revision >= self._limite_distance_parcourue_avant_revision \
                or pod.temps_depuis_revision >= self._limite_temps_ecoule_avant_revision \
                or (pod.nombre_signalements_doit_aller_en_revision >= self._limite_nombre_signalements_avant_revision
                    and pod.dernier_signalement_revision_par_vrai_utilisateur)
