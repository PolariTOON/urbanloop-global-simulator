"""
Cette classe permet de gérer le code lié à un lancement d'une simulation sans interface graphique
"""
from asyncio import get_running_loop, run
from json import load
from threading import Thread

from controler.simulation import Simulation

_network_file = "resources/new_mini_network.json"  # TODO: mettre cette ou ces valeurs en paramètre du programme
_sim_tick = 0.042  # TODO: mettre cette ou ces valeurs en paramètre du programme
_loop = None
_simulations = {}


async def _run_simulations():
    """Lancement de simulations"""
    print("Log format : receiver  --  author  --  message type")
    global _sim_tick
    global _loop
    global _simulations
    _loop = get_running_loop()
    while True:
        for key in _simulations:
            simulation = _simulations[key]
            simulation.update()


def run_app():
    with open(_network_file) as file:
        network_index = 0
        network_item = load(file)
    if network_item is not None:
        if "id" in network_item:
            del network_item["id"]
        simulation = Simulation(network_index, _sim_tick, **network_item)
        _simulations[network_index] = simulation
    elif network_index in _simulations:
        del _simulations[network_index]
    Thread(target=lambda: run(_run_simulations())).start()
