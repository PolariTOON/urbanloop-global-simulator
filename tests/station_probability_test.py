from settings import config
from simulator import converter
from model.station import *

config.load('../resources/config.ini')
converter.load()

neutral_station = Station(station_type=Type.NEUTRAL)
city_station = Station(station_type=Type.CITY)
residential_station = Station(station_type=Type.RESIDENTIAL)
activity_station = Station(station_type=Type.ACTIVITY)

neutral_prob = []
city_prob = []
residential_prob = []
activity_prob = []

is_arrival = True

for hour in range(24):
    second = 3600 * hour
    neutral_prob.append(converter.station_probability(neutral_station, second, is_arrival=is_arrival))
    city_prob.append(converter.station_probability(city_station, second, is_arrival=is_arrival))
    residential_prob.append(converter.station_probability(residential_station, second, is_arrival=is_arrival))
    activity_prob.append(converter.station_probability(activity_station, second, is_arrival=is_arrival))

print("Neutral probabilities :")
print(neutral_prob)
print("City probabilities :")
print(city_prob)
print("Residential probabilities :")
print(residential_prob)
print("Activity probabilities :")
print(activity_prob)