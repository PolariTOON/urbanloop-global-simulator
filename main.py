from argparse import ArgumentParser, ArgumentTypeError #bibliothèque pour récupérer les arguments du main afin d'établir la simulation avec les paramètres en entrée
from math import isfinite
from app import run_app


def networks(value):
    """value contient un path de fichier json décrivant un réseau"""

    try:  # cas où plusieurs networks sont en paramètre
        global _networks0
        global nb_networks                  # si on a déjà utilisé la fonction, nb_networks existe et on augmente le compteur
        nb_networks = nb_networks + 1
    except NameError:                       # sinon on initialise les variables
        _networks0 = {}
        nb_networks = 0

    if value == "{}":
        return {}
    try:  # vérification de l'existence du fichier
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


if __name__ == '__main__':
    argument_parser = ArgumentParser(description="Run the UrbanLoop simulator")
    argument_parser.add_argument("-n", "--networks", nargs= '+', type=networks, default="{}", help="load the given networks or none by default, the path should be given for each network")
    argument_parser.add_argument("-p", "--port", type=port, default=-1, const=8090, nargs='?', help="run a web application on the given port or 8090 by default")
    argument_parser.add_argument("-w", "--wave", type=wave, default=.042, help="set the duration of each wave to the given value (in seconds) or .042 seconds by default")
    arguments = argument_parser.parse_args()

    if arguments.networks != {}:
        arguments.networks = arguments.networks[0]  # à cause de nargs= '+' on a une liste en sortie, donc je ne garde que le dictionnaire des réseaux

    print("test")
    run_app(arguments.port, arguments.networks, arguments.wave)
