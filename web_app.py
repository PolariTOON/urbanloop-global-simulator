"""
Cette classe permet de gérer le code lié à un lancement d'une simulation avec interface graphique
"""
from asyncio import get_running_loop, run, run_coroutine_threadsafe, sleep
from flask import Flask, jsonify, request
from flask.json import load, loads
from functools import wraps
from logging import ERROR, getLogger
from threading import Thread

from controler.simulation import Simulation
from model import loop, routing, station, switch, warehouse, capsule, sensor
from settings import config, network, simlog
from simulator import sim_loop, converter

_app = Flask(__name__, static_url_path="", static_folder="view/static", template_folder="view/templates")
_app.logger.setLevel(ERROR)
getLogger("werkzeug").setLevel(ERROR)
sim_thread = None

_loop = None
_simulations = {}


def _load_new_mini_network():  # TODO: retirer
    global _simulations
    with open("resources/new_mini_network.json") as file:
        kwargs = load(file)
        _simulations[0] = Simulation(0, **kwargs)


async def _run_simulations():
    global _loop
    global _simulations
    _loop = get_running_loop()
    _load_new_mini_network()
    while True:
        await sleep(.5)  # TODO: calculer selon la vitesse et la précision de la simulation, ainsi que l'occupation du serveur
        for key in _simulations:
            simulation = _simulations[key]
            simulation.update()


def _synchronize(key=None):
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
            except Exception:
                result = None
            return jsonify(result)
        return routine
    return synchronize


@_app.errorhandler(Exception)
def send_error(error):
    global _app
    _app.logger.error(error)
    return "", 404


@_app.route("/")
def get_root():
    global _app
    return _app.send_static_file("index.html")


@_app.route("/new/")
def get_new_root():
    global _app
    return _app.send_static_file("new/index.html")


@_app.route('/clock/', methods=['GET'])
def get_clock():
    return jsonify(converter.serialize_clock())


@_app.route('/clock/start/', methods=['POST'])
def start_clock():
    global sim_thread
    if sim_thread is None:
        network.init_capsules()
        sim_thread = Thread(target=sim_loop.start_simulation, args=[True])
        sim_thread.start()
    return ''


@_app.route('/clock/stop/', methods=['POST'])
def stop_clock():
    global sim_thread
    if sim_thread is not None:
        sim_thread = None
        sim_loop.stop_simulation()
    return ''


@_app.route('/clock/pause/', methods=['POST'])
def pause_clock():
    global sim_thread
    if sim_thread is not None and not sim_loop.is_paused():
        sim_loop.pause_simulation()
    return ''


@_app.route('/clock/resume/', methods=['POST'])
def resume_clock():
    global sim_thread
    if sim_thread is not None and sim_loop.is_paused():
        sim_loop.run_simulation_after_pause()
    return ''


@_app.route('/clock/accelerate/', methods=['POST'])
def accelerate_clock():
    global sim_thread
    if sim_thread is not None:
        sim_loop.accelerate_simulation()
    return ''


@_app.route('/clock/decelerate/', methods=['POST'])
def decelerate_clock():
    global sim_thread
    if sim_thread is not None:
        sim_loop.decelerate_simulation()
    return ''


@_app.route('/loops/', methods=['GET'])
def get_loops():
    return jsonify([a_loop.serialize() for a_loop in loop.get_loops()])


@_app.route('/stations/', methods=['GET'])
def get_stations():
    return jsonify([a_station.serialize() for a_station in station.get_stations()])


@_app.route('/warehouses/', methods=['GET'])
def get_warehouses():
    return jsonify([a_warehouse.serialize() for a_warehouse in warehouse.get_warehouses()])


@_app.route('/switches/', methods=['GET'])
def get_switches():
    return jsonify([a_switch.serialize() for a_switch in switch.get_switches()])


@_app.route('/sensors/', methods=['GET'])
def get_sensors():
    return jsonify([a_sensor.serialize() for a_sensor in sensor.get_sensors()])


@_app.route('/data/', methods=['GET'])
def get_data():
    list_clock_data = [converter.serialize_clock()]
    list_station_var_data = [a_station.serialize() for a_station in station.get_stations()]
    list_warehouse_var_data = [a_warehouse.serialize() for a_warehouse in warehouse.get_warehouses()]
    list_switch_var_data = [a_switch.serialize() for a_switch in switch.get_switches()]
    list_capsule_data = [a_capsule.serialize() for a_capsule in capsule.get_capsules()]
    list_sensor_data = [a_sensor.serialize() for a_sensor in sensor.get_sensors()]
    return jsonify(
        list_clock_data + list_station_var_data + list_warehouse_var_data + list_switch_var_data + list_capsule_data + list_sensor_data)


@_app.route('/networks/', methods=['GET'])
def get_networks():
    network_file_names = [network.serialize_network_file_name(network_file_name) for network_file_name in
                          network.get_network_file_names()]
    return jsonify(network_file_names)


@_app.route('/networks/<string:file_name>/', methods=['GET'])
def get_network(file_name):
    return jsonify(network.get_network_json(file_name))


@_app.route('/networks/<string:file_name>/load/', methods=['POST'])
def load_network(file_name):
    global sim_thread
    if sim_thread is None:
        network.load(file_name=file_name, capsules_fulfill=False)
    return jsonify(network.serialize_network_size())


@_app.route('/networks/<string:file_name>/add/', methods=['POST'])
def add_network(file_name):
    network.add_network_file(file_name, loads(request.form['data']))
    return ''


@_app.route('/networks/<string:file_name>/remove/', methods=['POST'])
def remove_network(file_name):
    network.remove_network_file(file_name)
    return ''


@_app.route('/config/', methods=['GET'])
def get_config():
    return jsonify(config.serialize_config())


@_app.route('/config/reset/', methods=['POST'])
def reset_config():
    config.reset_config()
    routing.init_routing()
    switch.init_switch()
    converter.init_converter()
    simlog.load()
    return ''


@_app.route('/config/save/', methods=['POST'])
def save_config():
    config.save_config(loads(request.form['data']))
    routing.init_routing()
    switch.init_switch()
    converter.init_converter()
    simlog.load()
    return ''


@_app.route('/config/restore/', methods=['POST'])
def restore_config():
    config.restore_config()
    routing.init_routing()
    switch.init_switch()
    converter.init_converter()
    simlog.load()
    return ''


@_app.route("/networks/<int:network_index>/", methods=["POST"])
@_synchronize("network_item")
async def _post_network(simulations, network_index, network_item):
    if network_item is not None:
        simulation = Simulation(network_index, **network_item)
        simulations[network_index] = simulation
        return simulation.serialize()
    if network_index in simulations:
        del simulations[network_index]
    return None


@_app.route("/networks/<int:network_index>/", methods=["GET"])
@_synchronize()
async def _get_network(simulations, network_index):
    if network_index in simulations:
        simulation = simulations[network_index]
        return simulation.serialize()
    return None


@_app.route("/networks/<int:network_index>/clock/play/", methods=["POST"])
@_synchronize()
async def _play_clock(simulations, network_index):
    if network_index in simulations:
        simulation = simulations[network_index]
        simulation.running = True
        return True
    return False


@_app.route("/networks/<int:network_index>/clock/pause/", methods=["POST"])
@_synchronize()
async def _pause_clock(simulations, network_index):
    if network_index in simulations:
        simulation = simulations[network_index]
        simulation.running = False
        return True
    return False


@_app.route("/networks/<int:network_index>/bridges/<int:bridge_index>/", methods=["GET"])
@_synchronize()
async def _get_bridge(simulations, network_index, bridge_index):
    return simulations[network_index]._controler._network.bridges[bridge_index].serialize()


@_app.route("/networks/<int:network_index>/loops/<int:loop_index>/", methods=["GET"])
@_synchronize()
async def _get_loop(simulations, network_index, loop_index):
    return simulations[network_index]._controler._network.loops[loop_index].serialize()


@_app.route("/networks/<int:network_index>/switches/<int:switch_index>/", methods=["GET"])
@_synchronize()
async def _get_switch(simulations, network_index, switch_index):
    return simulations[network_index]._controler._network.switches[switch_index].serialize()


@_app.route("/networks/<int:network_index>/routes/<int:route_index>/", methods=["GET"])
@_synchronize()
async def _get_route(simulations, network_index, route_index):
    return simulations[network_index]._controler._network.routes[route_index].serialize()


@_app.route("/networks/<int:network_index>/routes/<int:route_index>/steps/<int:step_index>/", methods=["GET"])
@_synchronize()
async def _get_step(simulations, network_index, route_index, step_index):
    return simulations[network_index]._controler._network.routes[route_index].steps[step_index].serialize()


@_app.route("/networks/<int:network_index>/routes/<int:route_index>/sections/<int:section_index>/", methods=["GET"])
@_synchronize()
async def _get_section(simulations, network_index, route_index, section_index):
    return simulations[network_index]._controler._network.routes[route_index].sections[section_index].serialize()


def run_app(port):
    print("App running on port %d (http://127.0.0.1:%d)" % (port, port))
    print("Static loading of the new json file (http://127.0.0.1:%d/new/)" % port)
    Thread(target=lambda: run(_run_simulations())).start()
    _app.run(port=port)
