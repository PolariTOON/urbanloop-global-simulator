import model.loop
from model import switch as model_switch
from settings import config

timer_other = None
my_timer = None
switched_cost = None


def init_routing():
    global timer_other
    global my_timer
    global switched_cost
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
    for l, sw in to_cover.items():
        table_to_cover[l] = [sw] + table[l]

    # on veut calculer tous les chemins
    while table_to_cover != {}:
        # on récupère dans step la table vers la section qu'il reste à visiter avec le cout le plus faible
        step = []
        min_cost = float('Inf')
        for l, t in table_to_cover.items():
            if t[2] < min_cost:
                step = [l] + t
                min_cost = t[2]
        # format de step : ["loop", switch_id, to_switch, cost, [path]]
        del table_to_cover[step[0]]

        # on ajoute la découverte à la table
        loop = model.loop.get_by_name(step[0].split("_")[0])
        the_switch = model_switch.get_switch_by_id(step[1])

        next_switch = model_switch.get_switch_by_id(int(float(step[0].split("_")[1].split("-")[1])))
        if next_switch is not the_switch:
            distance = step[3] + loop.distance_between(the_switch, next_switch)
            if next_switch.other_loop is loop:
                # c'est un switch in : on reste sur la même boucle pour y aller mais on ajoute le cout
                if next_switch.section_other_loop not in table_temp or distance < \
                        table_temp[next_switch.section_other_loop][1]:
                    table_temp[next_switch.section_other_loop] = [step[2], distance, step[4] + [next_switch.id,
                                                                                                next_switch.section_other_loop]]
                    if next_switch.section_other_loop not in table_to_cover or distance < \
                            table_to_cover[next_switch.section_other_loop][2]:
                        table_to_cover[next_switch.section_other_loop] = [next_switch.id] + table_temp[
                            next_switch.section_other_loop]
            elif next_switch.my_loop is loop:
                # on a bien affaire a un switch aiguillant depuis la boucle --> on doit parcourir à partir de next_switch
                if not switch.defects[next_switch.id][0]:
                    # il n'y a pas d'anomalies pour rester sur la boucle
                    if next_switch.section_my_loop not in table_temp or distance < \
                            table_temp[next_switch.section_my_loop][1]:
                        table_temp[next_switch.section_my_loop] = [step[2], distance, step[4] + [next_switch.id,
                                                                                                 next_switch.section_my_loop]]
                        if next_switch.section_my_loop not in table_to_cover or distance < \
                                table_to_cover[next_switch.section_my_loop][2]:
                            table_to_cover[next_switch.section_my_loop] = [next_switch.id] + table_temp[
                                next_switch.section_my_loop]

                if not switch.defects[next_switch.id][1]:
                    # il n'y a pas d'anomalies dans la boucle aiguillee
                    distance += next_switch.size + switched_cost
                    if next_switch.section_other_loop not in table_temp or distance < \
                            table_temp[next_switch.section_other_loop][1]:
                        table_temp[next_switch.section_other_loop] = [step[2], distance, step[4] + [next_switch.id,
                                                                                                    next_switch.section_other_loop]]
                        if next_switch.section_other_loop not in table_to_cover or distance < \
                                table_to_cover[next_switch.section_other_loop][2]:
                            table_to_cover[next_switch.section_other_loop] = [next_switch.id] + table_temp[
                                next_switch.section_other_loop]

    return table_temp
