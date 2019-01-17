#! /usr/bin/env python3
# coding: utf-8

import model.loop
from settings import config

timer_other = int(config.routing['timer_other'])
my_timer = int(config.routing['my_timer'])


def parcours(switch, table, to_cover):
    table_temp = table
    table_to_cover = {}
    for l, a in to_cover.items():
        table_to_cover[l] = [a] + table[l]
    # print(table_to_cover)
    while table_to_cover != {}:
        step = []
        min_cost = float('Inf')
        # print(min_cost)
        for l, t in table_to_cover.items():
            # print(t)
            if (t[2] < min_cost):
                step = [l] + t
                min_cost = t[2]
        # print(step)
        # ['loop XX', switch_id, to_switch, cost, [path]]
        del table_to_cover[step[0]]

        loop = model.loop.get_by_name(step[0])
        for next_switch in loop.switches:

            if next_switch.id != step[1] and (next_switch.id is not None):
                # vérifier que ce n'est pas déjà dans la table
                # --> pas besoin car sinon cout ++
                if not switch.defects[next_switch.id][0]:  # il n'y a pas d'anomalies pour rester sur la boucle
                    if (next_switch.my_loop.name) not in table_temp:
                        table_temp[next_switch.my_loop.name] = [step[2], step[3] + next_switch.size,
                                                                step[4] + [next_switch.id, next_switch.my_loop.name]]
                        # TODO 100 à remplacer par distance (switch, point suivant)
                        table_to_cover[next_switch.my_loop.name] = [next_switch.id] + table_temp[
                            next_switch.my_loop.name]
                if not switch.defects[next_switch.id][1]:  # il n'y a pas d'anomalies dans la boucle aiguillee
                    if (next_switch.switched_loop.name) not in table_temp:
                        table_temp[next_switch.switched_loop.name] = [step[2], step[3] + next_switch.size,
                                                                      step[4] + [next_switch.id,
                                                                                 next_switch.switched_loop.name]]
                        table_to_cover[next_switch.switched_loop.name] = [next_switch.id] + table_temp[
                            next_switch.switched_loop.name]
    return table_temp


def update_switch(s):
    info = None  # "alive", "0_down", "1_down", None

    return info
