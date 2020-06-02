"""
Cette classe permet de gérer le code lié à un lancement d'une simulation sans interface graphique
"""
from asyncio import get_running_loop, run, sleep
from json import load
from threading import Thread
from traceback import print_exc

from controler.simulation import Simulation

_wave = 0  # IDEA: calculer selon la vitesse et la précision des simulations
_loop = None
_simulations = {}


async def _run_simulations(networks, wave):
    """Lancement de simulations"""
    print("Log format : receiver  --  author  --  message type")
    global _wave
    global _loop
    global _simulations
    _wave = wave
    for network_index in networks:
        network_file = networks[network_index]
        with open(network_file) as file:
            network_item = load(file)
        if network_item is not None:
            if "id" in network_item:
                del network_item["id"]
            try:
                simulation = Simulation(network_index, _wave, **network_item)
                simulation.running = True
                _simulations[network_index] = simulation
            except Exception:
                print_exc()
    _loop = get_running_loop()
    while True:
        await sleep(_wave)
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


def run_app(networks, wave):
    Thread(target=lambda: run(_run_simulations(networks, wave))).start()
