import model.loop as ML
from settings import network

network.load()

for name, l in ML.all_loops.items():
    print("\n", l.name, l.x)
    print("\t", [st.name for st in l.stations])
    print("\t", [sw.id for sw in l.switches])
    print("\t", [[o[0], o[1].id, o[2]] for o in l.objects])
    for sw in l.switches:
        print("\t \t", sw.id, sw.table)
