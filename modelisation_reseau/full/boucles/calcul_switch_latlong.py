import sys

if len(sys.argv) == 3:
    # Ex :
    #   python  calcul_switch_latlong.py  48.625671  6.202622
    
    average_lat, average_long = sys.argv[1], sys.argv[2]
    
    latIN  = average_lat  - 0.0009
    longIN = average_long - 0.0009

    latOUT  = average_lat  + 0.0009
    longOUT = average_long + 0.0009
    
else:
    
    lat1 = 48.625671
    long1 = 6.202622

    lat2 = 48.624378
    long2 = 6.191177

    latIN = ((lat1 + lat2) / 2) - 0.0009
    longIN = ((long1 + long2) / 2) - 0.0009

    latOUT = ((lat1 + lat2) / 2) + 0.0009
    longOUT = ((long1 + long2) / 2) + 0.0009

print("Switch In : ", latIN,",", longIN)
print("Switch Out : ", latOUT,",", longOUT)

