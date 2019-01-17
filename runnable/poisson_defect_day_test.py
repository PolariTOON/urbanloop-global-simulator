from settings import config
from simulator import poisson


# TODO thibault specification


CONFIG_PATH = '../resources/config.ini'
config.load(CONFIG_PATH)

poisson = poisson.Poisson()

total = 0
for second in range(86400):
    total += poisson.defect()

print("Somme des résultats obtenus pour un jour :", total)

do_mean_on_100 = True
if do_mean_on_100:
    mean = 0
    for repeat in range(50):
        total = 0
        for second in range(86400):
            total += poisson.defect()
        mean += total
    mean = float(mean / 50)
    print("Moyenne des résultats obtenus pour 100 jour :", total)
