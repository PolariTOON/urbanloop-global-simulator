from argparse import ArgumentParser, ArgumentTypeError  # bibliothèque pour récupérer les arguments du main afin d'établir la simulation avec les paramètres en entrée
from app import run_app, set_defaut                 # fonction de lancement de l'application
from main import networks, port, wave                   # réutilisation du main
from test_project.Simulations import *


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ArgumentTypeError('Boolean value expected.')


if __name__ == '__main__':
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

    set_defaut(arguments.running, arguments.speed)

    if arguments.networks != {}:
        arguments.networks = arguments.networks[0]  # à cause de nargs= '+' on a une liste en sortie, donc je ne garde que le dictionnaire des réseaux
        for i in range(1, arguments.number):
            arguments.networks[i] = arguments.networks[0]
    run_app(arguments.port, arguments.networks, arguments.wave)
