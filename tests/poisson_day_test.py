from config import config
from simulator import poisson

CONFIG_PATH = '../resources/config.ini'
config.load(CONFIG_PATH)

poisson = poisson.Poisson()

total = 0
hour_density = []
for hour in range(24):
    hour_total = 0
    for second in range(3600):
        hour_total += poisson.generate(hour)
    hour_density.append(hour_total)
    total += hour_total

print("Tableau des totaux par heure :")
print(hour_density)
print("Somme des résultats obtenus :", total)
