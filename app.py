from asyncio import get_running_loop, run, sleep
from json import load
from threading import Thread
from traceback import print_exc
import signal

from controler.simulation import Simulation

"""Classe chargée de la réalisation de la simulation"""

_wave = 0  # IDEA: calculer selon la vitesse et la précision des simulations, ainsi que l'occupation du serveur
_loop = None
_simulations = {}
_remove_travelers = False

_running_default = False
_speed_default = 8  # but speed is also limited by simulation.max_rate

# handler for SIGINT (CTRL-C)
_quit = False
def quit_func(sig, frame):
    """ Quit the program """
    # stop `_run_simulations()`
    global _quit
    _quit = True
    # IDEA: we should maybe properly close Flask process before exiting ?
    exit(0)
signal.signal(signal.SIGINT, quit_func)

# init and main loop
async def _run_simulations(with_interface, networks, wave, remove_travelers):
    """ Lancement de simulation(s) """
    print("Log format : receiver  --  author  --  message type")
    global _wave
    global _loop
    global _simulations
    global _remove_travelers
    global _running_default
    global _speed_default

    _wave = wave
    _remove_travelers = remove_travelers
    if not with_interface:
        _running_default = True
    if not with_interface:
        #print("strating with ..." ...)
        #_speed_default = ...
        pass

    # lancement des simulations avec les réseaux préchargés
    for network_path in networks:
        try:
            with open(network_path) as file:
                network_item = load(file)
        except Exception: network_item = None
        if network_item is not None:
            if "id" in network_item:
                del network_item["id"]
            try:
                network_index = len(_simulations)
                simulation = Simulation(network_index, _wave, _remove_travelers, **network_item)
                _simulations[network_index] = simulation
                simulation.running = _running_default
                simulation.rate = _speed_default
            except Exception:
                print_exc()
    # main loop
    _loop = get_running_loop()
    while not _quit:
        if with_interface:
            await sleep(0.5) #0.04) # ralentit la simulation pour utiliser l'interface (0.04s -> 25 images par secondes)
        else:
            pass # à tester (remplacer par await sleep(0.000001) ?)
        crashed_simulations = []
        for key in _simulations:
            simulation = _simulations[key]
            try:
                #print("__")
                #print("now: %f" % float(simulation._env.now))
                #print("now: %f" % float(simulation._env.time))
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
    if port != -1:
        with_interface = True
    else:
        with_interface = False
    
    Thread(target=lambda: run(_run_simulations(with_interface, networks, wave, remove_travelers))).start()
    if with_interface:  # utilisation de l'interface web
        from config_Flask import run_app
        run_app(port, networks, wave)


def set_defaut(running, speed):
    """ permet de choisir une vitesse au lancement de la simulation et faire en sorte que la simulation soit déjà lancée """
    global _running_default
    _running_default = running
    global _speed_default
    _speed_default = speed
