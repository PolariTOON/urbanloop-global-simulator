from asyncio import get_running_loop, run, sleep
from json import load
from threading import Thread
from traceback import print_exc
import signal

from controler.simulation import Simulation
import modifjson

"""Classe chargée de la réalisation de la simulation"""

_wave = 0  # IDEA: calculer selon la vitesse et la précision des simulations, ainsi que l'occupation du serveur
_loop = None
_simulations = {}
_remove_travelers = False

_running_default = False
_speed_default = 7 # = simulation max rate

# handler for SIGINT (CTRL-C)
_quit = False
def quit_func(sig, frame):
    """ Quit the program """
    # stop `_run_simulations()`
    global _quit
    _quit = True
    # -> we should maybe properly close Flask process before exiting ?
    exit(0)
signal.signal(signal.SIGINT, quit_func)

# init and main loop
async def _run_simulations(networks, wave, remove_travelers):
    """ Lancement de simulation(s) """
    print("Log format : receiver  --  author  --  message type")
    global _wave
    global _loop
    global _simulations
    global _remove_travelers

    _wave = wave
    _remove_travelers = remove_travelers
    # lancement des simulations avec les réseaux préchargés
    for network_path in networks:
        try:
            with open(network_path) as file:
                network_item = load(file)
                network_item = modifjson.mod_station(network_item) # ajout des mini-boucles pour les dépôts et stations
        except Exception: network_item = None
        if network_item is not None:
            if "id" in network_item:
                del network_item["id"]
            try:
                network_index = len(_simulations)
                simulation = Simulation(network_index, _wave, _remove_travelers, **network_item)
                _simulations[network_index] = simulation
                global _running_default
                simulation.running = _running_default
                global _speed_default
                simulation.rate = _speed_default
            except Exception:
                print_exc()
    # main loop
    _loop = get_running_loop()
    while not _quit:
        if _wave > 0:
            await sleep(_wave) # ralentit la simulation pour utiliser l'interface
        crashed_simulations = []
        for key in _simulations:
            simulation = _simulations[key]
            try:
                simulation.update()
            except Exception:
                crashed_simulations.append(key)
                print_exc()
        for key in crashed_simulations:
            del _simulations[key]
    print("Terminated")


def run_app(port, networks, wave, remove_travelers):
    """ Fonction permettant de lancer l'application
     port: n° de port si on souhaite l'interface web (sinon -1)"
     networks: contient les réseaux préchargés"
     wave: contient la vitesse de tic de simulation"
    """

    Thread(target=lambda: run(_run_simulations(networks, wave, remove_travelers))).start()
    if port != -1:  # utilisation de l'interface web
        from config_Flask import run_app
        run_app(port, networks, wave)


def set_defaut(running, speed):
    """ permet de choisir une vitesse au lancement de la simulation et faire en sorte que la simulation soit déjà lancée """
    global _running_default
    _running_default = running
    global _speed_default
    _speed_default = speed
