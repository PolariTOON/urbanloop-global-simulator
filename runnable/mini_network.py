import model.loop as ML
from settings import network


"""fichier de test d'import d'un réseau """


network.load('../resources/mini_network.json')

# on charge toutes les boucles créées
for name, l in ML.all_loops.items():
    print("\n", l.name, l.size, l.x, l.y)
    print("\t Stations : ", [[st.name, st.id] for st in l.stations])
    print("\t  -- an object in the loop = [[nature, id, angle in the loop]] -- ")
    print("\t", [[o[0], o[1].id, o[2]] for o in l.objects])  # objects est un attributs des loops qui contient la succession des éléments
    for sw in l.switches:
        print("\t \t table of switch ", sw.id, " : ", sw.table)
    # print(l.lengths)

loop_nancy = ML.get_by_name("Nancy")
o = loop_nancy.objects[2][1]
# print(o)
dist, next = loop_nancy.dist_to_next_object(o)
print("\n next object after ", o.name, " is ", next, " at ", dist)
