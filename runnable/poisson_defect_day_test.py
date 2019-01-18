from simulator import poisson

"""
Test pour connaître le nombre moyen de défauts apparus aléatoirement
par jour, sur un total de 100 jours. 
"""

poisson = poisson.Poisson()

total = 0
for second in range(86400):
    total += poisson.defect()

print("Somme des résultats obtenus pour un jour :", total)

do_mean_on_100 = False
if do_mean_on_100:
    mean = 0
    for repeat in range(50):
        total = 0
        for second in range(86400):
            total += poisson.defect()
        mean += total
    mean = float(mean / 50)
    print("Moyenne des résultats obtenus pour 100 jours :", total)
