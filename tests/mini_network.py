from settings import load_network
import model.loop as ML


load_network.load('../resources/mini_network.json')

for name, l in ML.all_loops.items():
    print("\n", l.name, l.x)
    print("\t", [st.name for st in l.stations])
    print("\t", [sw.id for sw in l.switches])
    for sw in l.switches:
        print("\t \t", sw.id, sw.table)