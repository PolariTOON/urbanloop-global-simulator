from simulator import poisson

"""
Test pour connaître le nombre de voyageurs apparus
au cours d'une journée. Un total par heure est affiché.
"""

poisson = poisson.Poisson()

total = 0
hour_density = []
for hour in range(24):
    hour_total = 0
    for second in range(3600):
        hour_total += poisson.traveler(hour)
    hour_density.append(hour_total)
    total += hour_total

print("Tableau des totaux par heure :")
print(hour_density)
print("Somme des résultats obtenus :", total)
