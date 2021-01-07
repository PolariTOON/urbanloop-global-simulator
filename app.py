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
    global _quit
    _quit = True # stop `_run_simulations()`
    save_simulations()

# handler for SIGINT (CTRL-C)
signal.signal(signal.SIGINT, stop_app)
    

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
    global _duration

    if not with_interface:
        print("WARNING : dans app.py : en mode sans interface, il est recommandé d'utiliser speed=7 pour optimiser la génération des travelers.")

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
    i=0
    while not _quit:
        if with_interface:
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
            if simulation.env.now >= _duration / simulation.env.tick:
                terminated = True
        for key in crashed_simulations:
            del _simulations[key]
        if terminated:
            print("Simulation Terminated.")
            stop_app()

    await sleep(0.5) # important : redonne la main au serveur flask (on lui laisse le temps de se fermer)
    print("Terminated.")


def run_app(port, networks, wave, remove_travelers, duration=-1):
    """ Fonction permettant de lancer l'application
     port: n° de port si on souhaite l'interface web (sinon -1)"
     networks: contient les réseaux préchargés"
     wave: contient la vitesse de tic de simulation"
    """
    global _duration
    _duration = duration
    
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
