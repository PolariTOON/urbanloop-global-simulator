#! /usr/bin/env python3
# coding: utf-8

import model.loop
from settings import config

timer_other = int(config.routing['timer_other'])
my_timer = int(config.routing['my_timer'])


def dijkstra_route(switch, table, to_cover):
    """
     (re)calcul de la table des chemins optimaux à partir d'un switch
        :param  switch : switch auquel est rataché la table (Switch) OBLIGATOIRE
        :param  table : état actuel de la table a recalculer contenant pour chaque boucle son nom, le fait qu'il faille
                        ou non switcher, le cout du chemin, un tableau du chemin
                        (Dictionnary : {string : [bool, float, [id/String]]}) OBLIGATOIRE
        :param  to_cover : le reste des boucle à explorer au format {boucle : ID aiguillage d'arrivée} ({String:int}
                        OBLIGATOIRE
        :return: 0UT : la table (re)calculée ({string : [bool, float, [id/String]]})
    """
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
            if t[2] < min_cost:
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
                    if next_switch.my_loop.name not in table_temp:
                        table_temp[next_switch.my_loop.name] = [step[2], step[3] + next_switch.size,
                                                                step[4] + [next_switch.id, next_switch.my_loop.name]]
                        table_to_cover[next_switch.my_loop.name] = [next_switch.id] + table_temp[
                            next_switch.my_loop.name]
                if not switch.defects[next_switch.id][1]:  # il n'y a pas d'anomalies dans la boucle aiguillee
                    if next_switch.other_loop.name not in table_temp:
                        table_temp[next_switch.other_loop.name] = [step[2], step[3] + next_switch.size,
                                                                   step[4] + [next_switch.id,
                                                                              next_switch.other_loop.name]]
                        table_to_cover[next_switch.other_loop.name] = [next_switch.id] + table_temp[
                            next_switch.other_loop.name]
    return table_temp


def update_switch(s):
    """
    mise à jour de la table en fonction des données reçues ou non + envoie de notre état
        :param  s : switch a tester et impacter (Switch) OBLIGATOIRE
        :return: 0UT : notre information (String : 'alive', '0_down', '1_down' ou None )
    """
    info = None  # "alive", "0_down", "1_down", None
    # TODO charlotte implemtantion
    return info
