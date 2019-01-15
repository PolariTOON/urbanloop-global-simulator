import model.Routing
#table = {}
#table["loop1"] = [False, 0, [1, "loop1"]]
#table["loop2"] = [True, 20, [1, "loop2"]]
table = {"loop1": [False, 0, [1, "loop1"]], "loop2": [True, 20, [1, "loop2"]]}
a_parcourir = {"loop1": 1, "loop2": 1}
#print(table)
print(table["loop2"][2].__contains__(1))
#t = model.Routing.parcours(table, a_parcourir)
#print(t)
