import Model.Routing

table = {1: [False, 0, [1, 1]], 2: [True, 20, [1, 2]]}
a_parcourir = {1: 1, 2: 1}

t = Model.Routing.parcours(table, a_parcourir)
print(t)
