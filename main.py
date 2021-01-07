from argparse import ArgumentParser, ArgumentTypeError # bibliothèque pour récupérer les arguments du main afin d'établir la simulation avec les paramètres en entrée
from math import isfinite
from app import run_app


def network(value):
    """value contient un path de fichier json décrivant un réseau"""
    try: # vérification de l'existence du fichier
        open(value, 'r').close()
    except IOError:
        print("\u001b[31m", "Fichier inexistant: \"", value, "\"\u001b[0m")
    return value


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


def duration(value):
    '''
    wave = float(value)
    if ... :
        return wave
    raise ArgumentTypeError("%s is not a valid duration" % value)
    '''


if __name__ == '__main__':
    argument_parser = ArgumentParser(description="Run the UrbanLoop simulator")
    argument_parser.add_argument("-n", "--networks", nargs='+', type=network, default=[], help="load the given networks or none by default, the path should be given for each network")
    argument_parser.add_argument("-p", "--port", type=port, default=-1, const=8090, nargs='?', help="run a web application on the given port or 8090 by default")
    argument_parser.add_argument("-w", "--wave", type=wave, default=.042, help="set the duration of each wave to the given value (in seconds) or .042 seconds by default")
    argument_parser.add_argument("-e", "--empty", action="store_true", help="remove all the travelers (useful to test the mobile app)")
    arguments = argument_parser.parse_args()
    
    run_app(arguments.port, arguments.networks, arguments.wave, arguments.empty)

