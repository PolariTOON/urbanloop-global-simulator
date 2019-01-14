def parcours(switch, table, to_cover):
    table_temp = table
    table_to_cover = {}
    for l, a in to_cover.items():
        table_to_cover[l] = [a] + table[l]
    # print(table_to_cover)
    while table_to_cover != {}:
        chosen = []
        min_cost = 1000
        for l, t in table_to_cover.items():
            if (t[2] < min_cost):
                chosen = [l] + t
                min_cost = t[2]
        print(chosen)
        #['loop XX', switch_id, to_switch, cost, [path]]
        del table_to_cover[chosen[0]]

        if not switch.defects[chosen[1]][0]: #il n'y a pas d'anomalies pour rester sur la boucle
            table_temp()


    return table_temp
