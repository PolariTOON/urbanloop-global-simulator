from asyncio import get_running_loop, run, sleep
from json import load
from threading import Thread
from traceback import print_exc
import time
import signal

from controler.simulation import Simulation

"""Classe chargée de la réalisation de la simulation"""

_wave = 0  # IDEA: calculer selon la vitesse et la précision des simulations, ainsi que l'occupation du serveur
_loop = None
_simulations = {}
_remove_travelers = False
_with_interface = False

_running_default = False
_speed_default = 7  # but speed is also limited by simulation.max_rate
_duration = -1
_quit = False

def save_simulations():
    """ lors de la fermeture de l'application, sauvegarde l'état des réseaux dans le dossier `./save` """
    from manip_format import pretty_dump
    for key in _simulations:
        simulation = _simulations[key]
        outfile = "./save/%d.json" % key
        with open(outfile, 'w') as f:
            f.write(pretty_dump(simulation.serialize(), 2))

def stop_app(sig=None, frame=None):
    """ Quit the program """
    print("Closing app...")
    global _with_interface
    global _quit
    _quit = True # stop `_run_simulations()`
    save_simulations()
    if _with_interface:
        print("(the server will be closed when it will receive any GET/POST request)")

# handler for SIGINT (CTRL-C)
signal.signal(signal.SIGINT, stop_app)
    

# init and main loop
async def _run_simulations(networks):
    """ Lancement de simulation(s) """
    print("Log format : receiver  --  author  --  message type")
    global _loop
    global _simulations
    global _running_default
    global _speed_default
    global _with_interface
    global _duration

    if not _with_interface:
        print("WARNING : dans app.py : en mode sans interface, il est recommandé d'utiliser speed=7 pour optimiser la génération des travelers.")
    
    if not _with_interface:
        _running_default = True
    if not _with_interface:
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
    i=0
    while not _quit:
        if _with_interface:
            #print("sleep start")
            await sleep(0.04) # ralentit la simulation pour utiliser l'interface (0.04s -> 25 images par secondes)
            #print("sleep end")
        else:
            pass # à tester (remplacer par await sleep(0.000001) ?)
        crashed_simulations = []
        terminated = False
        for key in _simulations:
            simulation = _simulations[key]
            try:
                #print()
                #print("__")
                #print("update...")
                simulation.update()
                #print("updated" + str(i))
                i+=1
            except Exception:
                crashed_simulations.append(key)
                print_exc()
            # check if the simulation is terminated
            if _duration >= 0 and simulation.env.now * simulation.env.tick >= _duration:
                terminated = True
        for key in crashed_simulations:
            del _simulations[key]
        if terminated:
            print("A simulation reached its total duration.")
            stop_app()

    #print("Terminated.")


def run_app(port, networks, wave, remove_travelers, duration=-1):
    """ Fonction permettant de lancer l'application
     port: n° de port si on souhaite l'interface web (sinon -1)"
     networks: contient les réseaux préchargés"
     wave: contient la vitesse de tic de simulation"
    """
    global _remove_travelers
    global _with_interface
    global _duration
    global _wave
    _remove_travelers = remove_travelers
    _with_interface = port >= 0
    _duration = duration
    _wave = wave
    
    Thread(target=lambda: run(_run_simulations(networks))).start()
    if _with_interface:  # utilisation de l'interface web
        from config_Flask import run_app
        run_app(port, networks, wave)
    else:
        # the main thread needs to continue running in order to catch signals (such as CTRL-C)
        while not _quit:
            time.sleep(1.0)


def set_defaut(running, speed):
    """ permet de choisir une vitesse au lancement de la simulation et faire en sorte que la simulation soit déjà lancée """
    global _running_default
    _running_default = running
    global _speed_default
    _speed_default = speed
