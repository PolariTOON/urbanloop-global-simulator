import Model.Routing
#table = {}
#table["loop1"] = [False, 0, [1, "loop1"]]
#table["loop2"] = [True, 20, [1, "loop2"]]
table = {"loop1": [False, 0, [1, "loop1"]], "loop2": [True, 20, [1, "loop2"]]}
a_parcourir = {"loop1": 1, "loop2": 1}
#print(table)
t = Model.Routing.parcours(table, a_parcourir)
print(t)
