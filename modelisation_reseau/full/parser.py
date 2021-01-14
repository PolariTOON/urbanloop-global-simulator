import pandas as pd
import csv
import fileinput
import geopy.distance

def inArray(nomStation, tab):
    for elem in tab:
        if(elem[0])==nomStation:
            return True
    return False

def sup(elem,nTab,x):
    coords_1 = (elem[4],elem[5])
    for element in nTab:
        coords_2 = (element[1],element[2])
        d = geopy.distance.distance(coords_1, coords_2).m
        if d < x : 
            return False
    return True

df = pd.read_csv('stops.txt')
print(df)
tab = df.to_numpy()
print(tab[0])

nTab = []
for element in tab:
    #On vérifie qu'il n'y a pas une autre station avec le mm nom
    if not(inArray(element[2],nTab)):
        #On vérifie que la distance entre la nouvelle station et les autres est supérieure à x (en mètre)
        if sup(element,nTab,500):
            ligne = [element[2],element[4],element[5],1,True,""]
            nTab.append(ligne)

print(nTab[0])

with open('newStops.csv', 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    # If we want the intermediate file to be valid (according to the old format),
    # then we need to begin the loop with a switch.
    # Here we commented the addition of switches because we'll directly convert
    # the file to the new format.
    #writer.writerow(["Switch In 1-2",48.659513, 6.269170,1,"Switch_In",0])
    writer.writerows(nTab)
    #writer.writerow(["Switch Out 1-2",48.659513, 6.269190,1,"Switch_Out",0])
