from PIL import Image
from numpy import *
"""
permet de générer un fichier json qui correspond à un réseau
à partir d'un fichier csv contenant les stations, dépots et boucles du réseau
    > on attend l'entête suivante:
            nom de la station/latitude/longitude/numéro de boucle/station ou dépot/numero de pont (pour les switchs)
    > les éléments doivent être regroupés par boucle
    > les éléments d'une boucle doivent être 
        dans l'ordre de parcours d'une boucle en commençant pour un switch_in et finissant par un switch_out
"""



def create_json(filename):
    csvfile = open('resources/coordonnees_stations_bus_tram_Nancy.csv', 'r')
    print("generate ", filename)

    stations = []       # ensemble des noms de station/dépots
    latitudes = []      # latitudes
    longitudes = []     # longitudes
    boucles = []        # numéro de la boucle
    abscisses = []
    ordonnees = []
    is_station = []     # true si c'est une station, switch si c'est un switch et false si c'est un dépôt
    bridge_indices = {}

    for line in csvfile:
        if line != "\n":
            element = line.split(",")
            stations.append(element[0])             # ensemble des noms de station/dépots
            latitudes.append(float(element[1]))     # latitudes
            longitudes.append(float(element[2]))    # longitudes
            boucles.append(int(element[3]))         # numéro d'appartenance de boucle
            if element[4] == "True":
                is_station.append(True)     # true si c'est une station, switch pour un switch et false si c'est un dépôt
            elif element[4] == "Switch_In":
                is_station.append("switch_in")
                bridge_indices[element[0]] = element[5]
            elif element[4] == "Switch_Out":
                is_station.append("switch_out")
                bridge_indices[element[0]] = element[5]
            else:
                is_station.append(False)
    for i in bridge_indices.keys():
        bridge_indices[i] = bridge_indices[i].rstrip('\n')

    # Pour obtenir le centre de la carte et générer les abscisses et ordonnées correspondantes
    # milieu = [350,350]

    latitude_min = min(latitudes)
    latitude_max = max(latitudes)

    longitude_min = min(longitudes)
    longitude_max = max(longitudes)

    for i in range(len(latitudes)):
        abscisses.append(round((latitudes[i] - latitude_min) / (latitude_max - latitude_min) * 10000) + 50)
        ordonnees.append(round((longitudes[i] - longitude_min) / (longitude_max - longitude_min) * 5000) + 50)

    # pour afficher une preview de la position des stations
    # pre_show_map(latitudes, latitude_min, latitude_max, longitude_min, longitude_max, longitudes, abscisses, ordonnees, is_station, boucles)

    jsonfile = open('resources/Grand_Nancy_8_boucles.json', 'w')
    jsonfile.write("{\n\"name\": \"Grand Nancy\",\n\"time\": 28800,\n\"state\": 56565,\n\"jerky\": true,\n\"running\": false,\n\"margin_min\": 2,\n\"max_speed\": 30,\n\"pod_size\": 2,\n\"places_number\": 5,\n\"dynamic_routing\": false,\n\"view_box\": {\n\t\"x\": 0,\n\t\"y\": 200,\n\t\"width\": 600,\n\t\"height\": 500\n},\n")   # entete du fichier

    # écriture de la partie loops
    loops = "\"loops\": [\n"

    for boucle0 in list(set(boucles)):
        loops += "\t{\"name\": \"" + str(boucle0) + "\",\n\t\"elements\": ["
        compteur = 0
        for i in range(len(boucles)):
            if boucles[i] == boucle0:
                compteur += 1
                if is_station[i] == "switch_in":
                    loops += "\n\t\t{\"type\": \"" + "switch_in" + "\", \"x\":" + str(abscisses[i]) \
                             + ",\"y\":" + str(ordonnees[i]) \
                             + ",\"id_bridge\": " + str(bridge_indices[stations[i]]) + ", \"pods\": []},"
                elif is_station[i] == "switch_out":
                    loops += "\n\t\t{\"type\": \"" + "switch_out" + "\", \"x\":" + str(abscisses[i]) \
                             + ",\"y\":" + str(ordonnees[i]) \
                             + ",\"id_bridge\": " + str(bridge_indices[stations[i]]) + ", \"pods\": []},"
                elif is_station[i]:
                    loops += "\n\t\t{\"type\": \"" + "station" + "\", \"name\": \"" \
                             + stations[i] + "\",\"x\":" + str(abscisses[i]) \
                             + ",\"y\":" + str(ordonnees[i]) \
                             + ",\"pods\": {\"max\": 5, \"count\": 3}, \"station_type\": 0, " \
                               "\"travelers\": {\"count\": 0, \"average_waiting_time\": 0, \"all_time_count\": 0}},"
                else:
                    loops += "\n\t\t{\"type\": \"" + "shed" + "\", \"name\": \"" \
                             + stations[i] + "\",\"x\":" + str(abscisses[i]) \
                             + ",\"y\":" + str(ordonnees[i]) \
                             + ",\"pods\": {\"max\": 200, \"count\": 100}},"
        loops = loops[:-1]
        loops += "\n\t],\n"
        loops += "\t\"sections\": [\n"
        for i in range(compteur - 1):
            loops += "\t\t{\"speed\": 20.00, \"path\": {\"type\": \"line\"}},\n"
        loops += "\t\t{\"speed\": 20.00, \"path\": {\"type\": \"line\"}}\n\t]," \
                 "\n\t\"pods\": []\n" \
                 "\t},\n"
    loops = loops[:-2]
    loops += "\n],\n"

    jsonfile.write(loops)

    # écriture de la partie bridges


    bridges = "\t\"bridges\": [\n"

    for bridge0 in bridge_indices.keys():
        if len(bridge0) == 13:  # c'est les switch in
            bridges += "\t\t{\"name\": \"Bridge " + bridge0[-3:] + "\", \"section\": {\"speed\": 19.44," \
                                                            " \"path\": {\"type\": \"line\"}}, \"pods\": []},\n"
    bridges = bridges[:-2]
    bridges += "\n\t]\n}"
    ####################

    jsonfile.write(bridges)

    jsonfile.close()


def pre_show_map(latitudes, latitude_min, latitude_max, longitude_min, longitude_max, longitudes, abscisses, ordonnees, is_station, boucles):
    ########### aperçu de la carte ############
    image0 = zeros((280000, 140000, 3), dtype=uint8)

    for i in range(len(latitudes)):
        if is_station[i] == "switch_in" or is_station[i] == "switch_out":
            for j in range(5):
                for k in range(5):
                    image0[abscisses[i] + j - 2][ordonnees[i] + k - 2] = [237, 127, 16]
        elif is_station[i]:
            for j in range(20):
                for k in range(20):
                    if boucles[i] == 1:
                        image0[abscisses[i] + j - 10][ordonnees[i] + k - 10] = [255, 255, 255]
                    elif boucles[i] == 2:
                        image0[abscisses[i] + j - 10][ordonnees[i] + k - 10] = [255, 255, 0]
                    elif boucles[i] == 3:
                        image0[abscisses[i] + j - 10][ordonnees[i] + k - 10] = [0, 255, 255]
                    elif boucles[i] == 4:
                        image0[abscisses[i] + j - 10][ordonnees[i] + k - 10] = [255, 0, 255]
                    elif boucles[i] == 5:
                        image0[abscisses[i] + j - 10][ordonnees[i] + k - 10] = [0, 0, 255]
                    elif boucles[i] == 6:
                        image0[abscisses[i] + j - 10][ordonnees[i] + k - 10] = [0, 255, 0]
                    elif boucles[i] == 7:
                        image0[abscisses[i] + j - 10][ordonnees[i] + k - 10] = [255, 255, 0]
                    elif boucles[i] == 8:
                        image0[abscisses[i] + j - 10][ordonnees[i] + k - 10] = [0, 255, 255]
                    else:
                        image0[abscisses[i] + j - 10][ordonnees[i] + k - 10] = [255, 255, 255]
        else:
            for j in range(20):
                for k in range(20):
                    image0[abscisses[i] + j - 10][ordonnees[i] + k - 10] = [255, 0, 0]

    imgpil = Image.fromarray(image0, 'RGB')
    imgpil.show()
    ########################################################


if __name__ == '__main__':
    nom_du_json = "Grand_Nancy.json"
    create_json(nom_du_json)