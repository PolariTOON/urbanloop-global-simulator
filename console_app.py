"""
Cette classe permet de gérer le code lié à un lancement d'une simulation sans interface graphique
"""
from asyncio import get_running_loop, run
from json import load
from threading import Thread

from controler.simulation import Simulation

_sim_tick = 0  # IDEA: calculer selon la vitesse et la précision des simulations
_loop = None
_simulations = {}


async def _run_simulations(networks, tick):
    """Lancement de simulations"""
    print("Log format : receiver  --  author  --  message type")
    global _sim_tick
    global _loop
    global _simulations
    _sim_tick = tick
    for network_index in networks:
        network_file = networks[network_index]
        with open(network_file) as file:
            network_item = load(file)
        if network_item is not None:
            if "id" in network_item:
                del network_item["id"]
            simulation = Simulation(network_index, _sim_tick, **network_item)
            _simulations[network_index] = simulation
    _loop = get_running_loop()
    while True:
        for key in _simulations:
            simulation = _simulations[key]
            simulation.update()


def run_app(networks, tick):
    Thread(target=lambda: run(_run_simulations(networks, tick))).start()
