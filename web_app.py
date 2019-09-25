from asyncio import get_running_loop, run, run_coroutine_threadsafe, sleep
from flask import Flask, jsonify, request
from functools import wraps
from json import load
from logging import ERROR, getLogger
from threading import Thread

from controler.simulation import Simulation


_app = Flask(__name__, static_url_path="", static_folder="view/static", template_folder="view/templates")
_app.logger.setLevel(ERROR)
getLogger("werkzeug").setLevel(ERROR)

_wave = 0  # IDEA: calculer selon la vitesse et la précision des simulations, ainsi que l'occupation du serveur
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
            simulation = Simulation(network_index, _wave, **network_item)
            _simulations[network_index] = simulation
    _loop = get_running_loop()
    while True:
        await sleep(_wave)
        for key in _simulations:
            simulation = _simulations[key]
            simulation.update()


def _synchronize(key=None):
    """Synchronisation du serveur flask avec simpy, NE PAS TOUCHER"""
    global _loop
    global _simulations
    if not isinstance(key, str):
        key = None

    def synchronize(coroutine):
        @wraps(coroutine)
        def routine(*args, **kwargs):
            if key is not None:
                kwargs[key] = request.get_json()
            try:
                result = run_coroutine_threadsafe(coroutine(_simulations, *args, **kwargs), _loop).result()
            except Exception as e:
                result = None
                print("\u001b[31m", e, "\u001b[0m")
            return jsonify(result)

        return routine

    return synchronize


@_app.errorhandler(Exception)
def send_error(error):
    """Gestion d'une mauvaise requête"""
    global _app
    _app.logger.error(error)
    return "", 404


@_app.route("/")
def get_root():
    """page de base de la vue"""
    global _app
    return _app.send_static_file("index.html")


@_app.route("/networks/<int:network_index>/", methods=["POST"])
@_synchronize("network_item")
async def _post_network(simulations, network_index, network_item):
    """Requête post pour envoyer et charger un réseau depuis la vue à partir d'un fichier json"""
    if network_item is not None:
        if "id" in network_item:
            del network_item["id"]
        simulation = Simulation(network_index, _wave, **network_item)
        simulations[network_index] = simulation
        return simulation.serialize()
    if network_index in simulations:
        del simulations[network_index]
    return None


@_app.route("/networks/<int:network_index>/", methods=["GET"])
@_synchronize()
async def _get_network(simulations, network_index):
    """Requête get pour récupérer le fichier json d'un réseau depuis la vue"""
    if network_index in simulations:
        simulation = simulations[network_index]
        return simulation.serialize()
    return None


@_app.route("/networks/<int:network_index>/clock/play/", methods=["POST"])
@_synchronize()
async def _play_clock(simulations, network_index):
    """Requête post pour lancer la simulation depuis la vue"""
    if network_index in simulations:
        simulation = simulations[network_index]
        simulation.running = True
        return True
    return False


@_app.route("/networks/<int:network_index>/clock/pause/", methods=["POST"])
@_synchronize()
async def _pause_clock(simulations, network_index):
    """Requête post pour mettre en pause la simulation depuis la vue"""
    if network_index in simulations:
        simulation = simulations[network_index]
        simulation.running = False
        return True
    return False


@_app.route("/networks/<int:network_index>/clock/decelerate/", methods=["POST"])
@_synchronize()
async def _decelerate_clock(simulations, network_index):
    """Requête post pour décélerer la simulation depuis la vue"""
    if network_index in simulations:
        simulation = simulations[network_index]
        simulation.rate -= 1
        return True
    return False


@_app.route("/networks/<int:network_index>/clock/accelerate/", methods=["POST"])
@_synchronize()
async def _accelerate_clock(simulations, network_index):
    """Requête post pour accélrer la simulation depuis la vue"""
    if network_index in simulations:
        simulation = simulations[network_index]
        simulation.rate += 1
        return True
    return False


@_app.route("/networks/<int:network_index>/bridges/<int:bridge_index>/", methods=["GET"])
@_synchronize()
async def _get_bridge(simulations, network_index, bridge_index):
    """Requête get pour récupérer le fichier json d'un pont depuis la vue"""
    return simulations[network_index]._network.bridges[bridge_index].serialize()


@_app.route("/networks/<int:network_index>/loops/<int:loop_index>/", methods=["GET"])
@_synchronize()
async def _get_loop(simulations, network_index, loop_index):
    """Requête get pour récupérer le fichier json d'une boucle depuis la vue"""
    return simulations[network_index]._network.loops[loop_index].serialize()


@_app.route("/networks/<int:network_index>/switches/<int:switch_index>/", methods=["GET"])
@_synchronize()
async def _get_switch(simulations, network_index, switch_index):
    """Requêt get pour récupérer le fichier json d'un aiguillage depuis la vue"""
    return simulations[network_index]._network.switches[switch_index].serialize()


@_app.route("/networks/<int:network_index>/routes/<int:route_index>/", methods=["GET"])
@_synchronize()
async def _get_route(simulations, network_index, route_index):
    """Requête get pour récupérer le fichier json d'une route depuis la vue"""
    return simulations[network_index]._network.routes[route_index].serialize()


@_app.route("/networks/<int:network_index>/routes/<int:route_index>/steps/<int:step_index>/", methods=["GET"])
@_synchronize()
async def _get_step(simulations, network_index, route_index, step_index):
    """Requête get pour récupérer le fichier json d'une étape depuis la vue"""
    return simulations[network_index]._network.routes[route_index].steps[step_index].serialize()


@_app.route("/networks/<int:network_index>/routes/<int:route_index>/sections/<int:section_index>/", methods=["GET"])
@_synchronize()
async def _get_section(simulations, network_index, route_index, section_index):
    """Requête get pour récupérer le fichier json d'une section depuis la vue"""
    return simulations[network_index]._network.routes[route_index].sections[section_index].serialize()


def run_app(port, networks, wave):
    """Fonction permettant de lancer l'application"""
    print("App running on port %d (http://127.0.0.1:%d)" % (port, port))
    Thread(target=lambda: run(_run_simulations(networks, wave))).start()
    _app.run(port=port)
