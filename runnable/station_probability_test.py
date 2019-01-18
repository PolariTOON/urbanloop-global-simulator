from model.station import Type
from simulator import converter

"""
Test pour obtenir la probabilité de diriger un voyageur
sur un type de station au cours de la journée heure par heure.
is_arrival est un booléen qui détermine si on souhaite obtenir
la probabilité de départ ou d'arrivée à une station.
"""

neutral_prob = []
city_prob = []
residential_prob = []
activity_prob = []

is_arrival = False

for hour in range(24):
    second = 3600 * hour
    neutral_prob.append(converter.station_probability(Type.NEUTRAL, second, is_arrival=is_arrival))
    city_prob.append(converter.station_probability(Type.CITY, second, is_arrival=is_arrival))
    residential_prob.append(converter.station_probability(Type.RESIDENTIAL, second, is_arrival=is_arrival))
    activity_prob.append(converter.station_probability(Type.ACTIVITY, second, is_arrival=is_arrival))

print("Neutral probabilities :")
print(neutral_prob)
print("City probabilities :")
print(city_prob)
print("Residential probabilities :")
print(residential_prob)
print("Activity probabilities :")
print(activity_prob)
