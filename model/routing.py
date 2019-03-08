import model.loop
from settings import config

timer_other = int(config.routing['timer_other'])
my_timer = int(config.routing['my_timer'])
switched_cost = int(config.routing['switched_cost'])


def dijkstra_route(switch, table, to_cover):
    """
     (re)calcul de la table des chemins optimaux à partir d'un switch
        :param  switch : switch auquel est rataché la table (Switch) OBLIGATOIRE
        :param  table : état actuel de la table a recalculer contenant pour chaque boucle son nom, le fait qu'il faille
                        ou non switcher, le cout du chemin, un tableau du chemin
                        (Dictionnary : {string : [bool, float, [objectId/String]]}) OBLIGATOIRE
        :param  to_cover : le reste des boucle à explorer au format {boucle : ID aiguillage d'arrivée} ({String:int}
                        OBLIGATOIRE
        :return: 0UT : la table (re)calculée ({string : [bool, float, [objectId/String]]})
    """
    table_temp = table
    table_to_cover = {}
    # on actualise la table à parcourir
    for l, a in to_cover.items():
        table_to_cover[l] = [a] + table[l]

    # on veut calculer tous les chemins
    while table_to_cover != {}:
        # print(switch.objectId, table_to_cover)
        # on récupère dans step la table vers la station qu'il reste à visiter avec le cout le plus faible
        step = []
        min_cost = float('Inf')
        for l, t in table_to_cover.items():
            if t[2] < min_cost:
                step = [l] + t
                min_cost = t[2]
        # format de step : ['station XX', switch_id, to_switch, cost, [path]]
        del table_to_cover[step[0]]

        # on ajoute la découverte à la table
        loop = model.loop.get_by_name(step[0])
        for next_switch in loop.switches:
            # parcours de tous les switchs de la boucle
            if next_switch.id != step[1]:
                if next_switch.my_loop is loop:
                    # on a bien affaire a un switch aiguillant depuis la boucle
                    # on doit parcourir à partir de next_switch
                    if not switch.defects[next_switch.id][0]:
                        # il n'y a pas d'anomalies pour rester sur la boucle
                        if next_switch.my_loop.name not in table_temp:
                            distance, a = loop.dist_to_next_object(step[1], next_switch)
                            # print(distance)
                            table_temp[next_switch.my_loop.name] = [step[2],
                                                                    step[3] + distance,
                                                                    step[4] + [next_switch.id,
                                                                               next_switch.my_loop.name]]
                            if next_switch.my_loop.name not in table_to_cover:
                                table_to_cover[next_switch.my_loop.name] = [next_switch.id] + table_temp[
                                    next_switch.my_loop.name]

                    if not switch.defects[next_switch.id][1]:
                        # il n'y a pas d'anomalies dans la boucle aiguillee
                        new_loop = next_switch.other_loop
                        if new_loop.name not in table_temp:
                            distance, a = new_loop.dist_to_next_object(switch, next_switch)
                            # print(distance)
                            table_temp[new_loop.name] = [step[2],
                                                         step[3] + distance + next_switch.size + switched_cost,
                                                         step[4] + [next_switch.id, next_switch.other_loop.name]]
                            if next_switch.my_loop.name not in table_to_cover:
                                table_to_cover[next_switch.other_loop.name] = [next_switch.id] + table_temp[next_switch.other_loop.name]
                            else:
                                # on regarde si c'est plus faible
                                if table_temp[next_switch.other_loop.name][1] > table_to_cover[3]:
                                    table_to_cover[next_switch.other_loop.name] = [next_switch.id] + table_temp[
                                        next_switch.other_loop.name]

                # else :
                # le calcul n'a pas à se faire maintenant
    # print(table_temp)
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
