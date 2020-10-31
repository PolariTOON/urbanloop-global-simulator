from asyncio import get_running_loop, run, sleep
from json import load
from threading import Thread
from traceback import print_exc

from controler.simulation import Simulation
import modifjson

"""Classe chargée de la réalisation de la simulation"""

_wave = 0  # IDEA: calculer selon la vitesse et la précision des simulations, ainsi que l'occupation du serveur
_loop = None
_simulations = {}
_remove_travelers = False

_running_default = False
_speed_default = 0


async def _run_simulations(networks, wave, remove_travelers):
    """Lancement de simulations"""
    print("Log format : receiver  --  author  --  message type")
    global _wave
    global _loop
    global _simulations
    global _remove_travelers

    _wave = wave
    _remove_travelers = remove_travelers
    for network_index in networks: # lancement des simulations avec les réseaux préchargés
        network_file = networks[network_index]
        with open(network_file) as file:
            network_item = load(file)
            network_item = modifjson.mod_station(network_item) # ajout des mini-boucles pour les dépôts et stations
        if network_item is not None:
            if "id" in network_item:
                del network_item["id"]
            try:
                simulation = Simulation(network_index, _wave, _remove_travelers, **network_item)
                _simulations[network_index] = simulation
                global _running_default
                simulation.running = _running_default
                global _speed_default
                simulation.rate = _speed_default
            except Exception:
                print_exc()
    _loop = get_running_loop()
    while True:
        # await sleep(_wave)  # utile pour ralentir une simulation pour utiliser l'interface
        await sleep(0.000001)
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


def run_app(port, networks, wave, remove_travelers):
    """Fonction permettant de lancer l'application"""
    "port = n° de port si on souhaite l'interface web (sinon -1)"
    "networks contient les réseaux préchargés"
    "wave contient la vitesse de tic de simulation"

    Thread(target=lambda: run(_run_simulations(networks, wave, remove_travelers))).start()
    if port != -1:  # utilisation de l'interface web
        from config_Flask import run_app
        run_app(port, networks, wave)


def set_defaut(running, speed):
    "permet de choisir une vitesse au lancement de la simulation et faire en sorte que la simulation soit déjà lancée"
    global _running_default
    _running_default = running
    global _speed_default
    _speed_default = speed
