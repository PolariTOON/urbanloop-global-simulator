from argparse import ArgumentParser, ArgumentTypeError #bibliothèque pour récupérer les arguments du main afin d'établir la simulation avec les paramètres en entrée
from math import isfinite

from test_project.Simulations import *


def networks(value):
    '''value contient un json avec comme items les numéros de réseaux et comme valeur le réseau associé à chaque numéro'''

    try: # cas où plusieurs networks sont en paramètre
        global _networks0
        global nb_networks                  # si on a déjà utilisé la fonction network existe et on augmente le compteur
        nb_networks = nb_networks + 1
    except NameError:                       # sinon on initialise les variables
        _networks0 = {}
        nb_networks = 0

    if value == "{}":
        return {}
    try:    # vérification de l'existence du fichier
        with open(value): pass
        _networks0[nb_networks] = value
    except IOError:
        print("\u001b[31m", "Fichier inexistant: ", value, "\u001b[0m")
        nb_networks = nb_networks - 1
    networks = _networks0
    return networks


def port(value):
    '''value contient la valeur du port que l'on souhaite utiliser, on vérifie que le numéro de port est correct'''
    port = int(value)
    if 0 <= port < 65536:
        return port
    raise ArgumentTypeError("%s is not a valid port" % value)


def wave(value):
    '''même chose que pour le port'''
    wave = float(value)
    if 0 < wave and isfinite(wave):
        return wave
    raise ArgumentTypeError("%s is not a valid wave" % value)

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ArgumentTypeError('Boolean value expected.')


argument_parser = ArgumentParser(description="Run multiple simulations")
argument_parser.add_argument("-n", "--networks", nargs= '+', type=networks, default="{}", help="load the given networks or none by default, the path should be given for each network")
argument_parser.add_argument("-p", "--port", type=port, default=-1, const=8090, nargs='?', help="run a web application on the given port or 8090 by default")
argument_parser.add_argument("-w", "--wave", type=wave, default=.042, help="set the duration of each wave to the given value (in seconds) or .042 seconds by default")
argument_parser.add_argument("-nb", "--number", type=int, default=0, help="number of simulations")
argument_parser.add_argument("-o", "--opentabs", type=str2bool, default=False, help="launch web windows if True")
argument_parser.add_argument("-r", "--running", type=str2bool, default=False, help="pre-selected simulations are running when tabs open")
argument_parser.add_argument("-s", "--speed", type=int, default=0, help="pre-selected simulations are running at this speed (0-7 -> x1-x128)")
arguments = argument_parser.parse_args()

if arguments.opentabs:
    thread = Simulations(arguments.port, arguments.number).start()

if arguments.port == -1:
    from console_app import run_app
    from web_app import set_defaut
    set_defaut(arguments.running, arguments.speed)

    if arguments.networks != {}:
        arguments.networks = arguments.networks[0]  # à cause de nargs= '+' on a une liste en sortie, donc je ne garde que le dictionnaire des réseaux
        for i in range(1, arguments.number):
            _networks0[i] = arguments.networks[0]

    run_app(arguments.networks, arguments.wave)
else:
    from web_app import run_app
    from web_app import set_defaut
    set_defaut(arguments.running, arguments.speed)

    arguments.networks = arguments.networks[
        0]  # à cause de nargs= '+' on a une liste en sortie, donc je ne garde que le dictionnaire des réseaux
    for i in range(1, arguments.number):
        _networks0[i] = arguments.networks[0]

    run_app(arguments.port, arguments.networks, arguments.wave)




