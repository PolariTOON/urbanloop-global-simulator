from controler.probability import Probability
from model.entities.nodes.networks.Statistiques import Statistiques
from simpy import Environment

"""
Script permettant de vérifier la bonne génération des voyageurs pendant la simulation
    - Vérifier le taux d'apparition de voyageurs en fonction de l'heure
    - Vérifier le taux d'apparition de voyageurs en fonction du type de station
    - Vérifier le nombre global d'apparition dans le réseau
"""

class Test_station:     # classe de substitution de station disposant des variables et fonctions nécessaires
    def __init__(self, station_type, name):
        self._station_type = station_type
        self.name = name
        self.travelers = []
        self.count = 0

    def up_all_time_count(self):
        self.count += 1

# 6 stations test, 2 par type
station1 = Test_station(0, "station1")
station2 = Test_station(0, "station2")
station3 = Test_station(1, "station3")
station4 = Test_station(1, "station4")
station5 = Test_station(2, "station5")
station6 = Test_station(2, "station6")

# j'ai repris ces paramètres des fichiers JSON de simulation
prob = {"activity_and_residential_percent": 50, "city_percent": 60, "activity_and_residential_fluctuation": 21}
traveler = {'travelers_per_day': 10000, 'morning_peak_hour': 8, 'evening_peak_hour': 18}
stations = [station1, station2, station3, station4, station5, station6]
statistiques = Statistiques()
tick = 0.042  # on peut le modifier et vérifier que les valeurs générées restent correctes


probability = Probability(prob, traveler, stations, statistiques, tick)
env = Environment()

Temps = 0
Printer = 0
last_cumul = 0

# Simulation
while Temps < 60*60*24:
    Temps += tick
    probability.generate_traveler_2(Temps, env)
    if Temps >= Printer:
        print(round(Temps)/3600, "h")
        cumul = 0
        for station in stations:
            print("\t", station.name, station.count)
            cumul += station.count
        print("hour generation", cumul - last_cumul)
        print("cumul =", cumul)
        print("\n")
        last_cumul = cumul
        Printer += 3600

print("\n\n-------------------------------\n")
print("Espérance du total =", traveler['travelers_per_day'], "/ cumul obtenu =", cumul)
print("Espérance par station / valeur simulée:")

# valeurs arbitraires utilisées dans probabilité, à changer si elles ont été modifiées
coefs = 0
coefs_stations = [0.1, 0.3, 0.5]
for station in stations:
    coefs += coefs_stations[station._station_type]

for i in range(len(stations)):
    print(stations[i].name, round(traveler['travelers_per_day']/coefs * coefs_stations[stations[i]._station_type]), "/", stations[i].count)