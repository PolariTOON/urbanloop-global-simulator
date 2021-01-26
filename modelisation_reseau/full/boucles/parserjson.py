import json



listBridge = [0] * 120

with open('modelisation_reseau/full/boucles/test.json') as json_file:
    data = json.load(json_file)
    for p in data['loops']:
        for elem in p['elements']:
            if elem['type']=="switch_in" or elem['type']=="switch_out":
                listBridge[elem['id_bridge']] += 1

for i in range(0,len(listBridge)):
    if(listBridge[i])!=2:
        print(i,listBridge[i])
    


