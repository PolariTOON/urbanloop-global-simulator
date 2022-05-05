class Gestionnaire:
    def __init__(self, network):
        self._network = network
        self._dict_revision_plus_proche = dict()
        self._dict_lavage_plus_proche = dict()
        self._dict_simple_plus_proche = dict()

    def obtenirDestination(self, station_source, categorie_destination):
        from ...network import shortest_way_tracks

        def longueur_chemin(chemin):
            longueur_totale = 0
            for i in range(len(chemin) - 1):
                if chemin[i + 1] is chemin[i].next:
                    longueur_totale += chemin[i].next.weight
                else:
                    longueur_totale += chemin[i].beside.weight
            return longueur_totale

        if categorie_destination == "HangarRevision":
            liste_hangars_possibles = self._network.hangarsRevision
            dict_hangars_plus_proches = self._dict_revision_plus_proche
        elif categorie_destination == "HangarLavage":
            liste_hangars_possibles = self._network.hangarsLavage
            dict_hangars_plus_proches = self._dict_lavage_plus_proche
        elif categorie_destination == "HangarSimple":
            liste_hangars_possibles = self._network.hangarsSimples
            dict_hangars_plus_proches = self._dict_simple_plus_proche
        else:
            raise ValueError(f"Catégorie {categorie_destination} non traitée dans obtenirDestinationDepuisHangarSimple de GestionnaireRevision")

        if station_source not in dict_hangars_plus_proches:

            if len(liste_hangars_possibles) > 1:
                hangar_plus_proche = liste_hangars_possibles[0]
                chemin = shortest_way_tracks(station_source, liste_hangars_possibles[0])
                longueur_chemin_plus_court = longueur_chemin(chemin)
                for i in range(1, len(liste_hangars_possibles)):
                    hangar_revision_possible = liste_hangars_possibles[i]
                    chemin = shortest_way_tracks(station_source, hangar_revision_possible)
                    longueur = longueur_chemin(chemin)
                    if longueur < longueur_chemin_plus_court:
                        hangar_plus_proche = hangar_revision_possible
                        longueur_chemin_plus_court = longueur

                dict_hangars_plus_proches[station_source] = hangar_plus_proche

            else:
                dict_hangars_plus_proches[station_source] = liste_hangars_possibles[0]

        return dict_hangars_plus_proches[station_source].name