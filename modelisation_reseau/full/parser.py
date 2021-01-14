import pandas as pd
import csv
import fileinput

def inArray(nomStation, tab):
    for elem in tab:
        if(elem[0])==nomStation:
            return True
    return False

df = pd.read_csv('stops.txt')
print(df)
tab = df.to_numpy()
print(tab[0])

nTab = []
for element in tab:
    if not(inArray(element[2],nTab)):
        ligne = [element[2],element[4],element[5],1,True,""]
        nTab.append(ligne)

print(nTab[1])

with open('newStops.csv', 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    # If we want the intermediate file to be valid (according to the old format),
    # then we need to begin the loop with a switch.
    # Here we commented the addition of switches because we'll directly convert
    # the file to the new format.
    #writer.writerow(["Switch In 1-2",48.659513, 6.269170,1,"Switch_In",0])
    writer.writerows(nTab)
    #writer.writerow(["Switch Out 1-2",48.659513, 6.269190,1,"Switch_Out",0])
