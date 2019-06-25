"""
Cette classe permet de gérer le code lié à un lancement d'une simulation avec interface graphique
"""

import logging
from threading import Thread

from flask import Flask, request, jsonify
from flask.json import loads

from controler.simulation import Simulation
from model import loop, routing, station, switch, warehouse, capsule, sensor
from settings import config, network, simlog
from simulator import sim_loop, converter

app = Flask(__name__, static_url_path="", static_folder='view/static', template_folder='view/templates')
app.logger.setLevel(logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.ERROR)
sim_thread = None

_simulations = []


def run_app(port):
    global _simulations
    print("App running on port %d (http://127.0.0.1:%d)" % (port, port))
    _simulations.append(Simulation(0))
    app.run(port=port)


@app.errorhandler(Exception)
def send_error(error):
    global app
    app.logger.error(error)
    return '', 404


@app.route('/')
def root():
    global app
    return app.send_static_file('index.html')


@app.route('/clock/', methods=['GET'])
def get_clock():
    return jsonify(converter.serialize_clock())


@app.route('/clock/start/', methods=['POST'])
def start_clock():
    global sim_thread
    if sim_thread is None:
        network.init_capsules()
        sim_thread = Thread(target=sim_loop.start_simulation, args=[True])
        sim_thread.start()
    return ''


@app.route('/clock/stop/', methods=['POST'])
def stop_clock():
    global sim_thread
    if sim_thread is not None:
        sim_thread = None
        sim_loop.stop_simulation()
    return ''


@app.route('/clock/pause/', methods=['POST'])
def pause_clock():
    global sim_thread
    if sim_thread is not None and not sim_loop.is_paused():
        sim_loop.pause_simulation()
    return ''


@app.route('/clock/resume/', methods=['POST'])
def resume_clock():
    global sim_thread
    if sim_thread is not None and sim_loop.is_paused():
        sim_loop.run_simulation_after_pause()
    return ''


@app.route('/clock/accelerate/', methods=['POST'])
def accelerate_clock():
    global sim_thread
    if sim_thread is not None:
        sim_loop.accelerate_simulation()
    return ''


@app.route('/clock/decelerate/', methods=['POST'])
def decelerate_clock():
    global sim_thread
    if sim_thread is not None:
        sim_loop.decelerate_simulation()
    return ''


@app.route('/loops/', methods=['GET'])
def get_loops():
    return jsonify([a_loop.serialize() for a_loop in loop.get_loops()])


@app.route('/stations/', methods=['GET'])
def get_stations():
    return jsonify([a_station.serialize() for a_station in station.get_stations()])


@app.route('/warehouses/', methods=['GET'])
def get_warehouses():
    return jsonify([a_warehouse.serialize() for a_warehouse in warehouse.get_warehouses()])


@app.route('/switches/', methods=['GET'])
def get_switches():
    return jsonify([a_switch.serialize() for a_switch in switch.get_switches()])


@app.route('/sensors/', methods=['GET'])
def get_sensors():
    return jsonify([a_sensor.serialize() for a_sensor in sensor.get_sensors()])


@app.route('/data/', methods=['GET'])
def get_data():
    list_clock_data = [converter.serialize_clock()]
    list_station_var_data = [a_station.serialize() for a_station in station.get_stations()]
    list_warehouse_var_data = [a_warehouse.serialize() for a_warehouse in warehouse.get_warehouses()]
    list_switch_var_data = [a_switch.serialize() for a_switch in switch.get_switches()]
    list_capsule_data = [a_capsule.serialize() for a_capsule in capsule.get_capsules()]
    list_sensor_data = [a_sensor.serialize() for a_sensor in sensor.get_sensors()]
    return jsonify(
        list_clock_data + list_station_var_data + list_warehouse_var_data + list_switch_var_data + list_capsule_data + list_sensor_data)


@app.route('/networks/', methods=['GET'])
def get_networks():
    network_file_names = [network.serialize_network_file_name(network_file_name) for network_file_name in
                          network.get_network_file_names()]
    return jsonify(network_file_names)


@app.route('/networks/<string:file_name>/', methods=['GET'])
def get_network(file_name):
    return jsonify(network.get_network_json(file_name))


@app.route('/networks/<string:file_name>/load/', methods=['POST'])
def load_network(file_name):
    global sim_thread
    if sim_thread is None:
        network.load(file_name=file_name, capsules_fulfill=False)
    return jsonify(network.serialize_network_size())


@app.route('/networks/<string:file_name>/add/', methods=['POST'])
def add_network(file_name):
    network.add_network_file(file_name, loads(request.form['data']))
    return ''


@app.route('/networks/<string:file_name>/remove/', methods=['POST'])
def remove_network(file_name):
    network.remove_network_file(file_name)
    return ''


@app.route('/config/', methods=['GET'])
def get_config():
    return jsonify(config.serialize_config())


@app.route('/config/reset/', methods=['POST'])
def reset_config():
    config.reset_config()
    routing.init_routing()
    switch.init_switch()
    converter.init_converter()
    simlog.load()
    return ''


@app.route('/config/save/', methods=['POST'])
def save_config():
    config.save_config(loads(request.form['data']))
    routing.init_routing()
    switch.init_switch()
    converter.init_converter()
    simlog.load()
    return ''


@app.route('/config/restore/', methods=['POST'])
def restore_config():
    config.restore_config()
    routing.init_routing()
    switch.init_switch()
    converter.init_converter()
    simlog.load()
    return ''


@app.route("/networks/<int:network_index>/", methods=["GET"])
def _get_network(network_index):
    global _networks
    return jsonify(_networks[network_index].serialize())


@app.route("/networks/<int:network_index>/bridges/<int:bridge_index>/", methods=["GET"])
def _get_bridge(network_index, bridge_index):
    global _networks
    return jsonify(_networks[network_index].bridges[bridge_index].serialize())


@app.route("/networks/<int:network_index>/loops/<int:loop_index>/", methods=["GET"])
def _get_loop(network_index, loop_index):
    global _networks
    return jsonify(_networks[network_index].loops[loop_index].serialize())


@app.route("/networks/<int:network_index>/switches/<int:switch_index>/", methods=["GET"])
def _get_switch(network_index, switch_index):
    global _networks
    return jsonify(_networks[network_index].switches[switch_index].serialize())


@app.route("/networks/<int:network_index>/routes/<int:route_index>/", methods=["GET"])
def _get_route(network_index, route_index):
    global _networks
    return jsonify(_networks[network_index].routes[route_index].serialize())


@app.route("/networks/<int:network_index>/routes/<int:route_index>/steps/<int:step_index>/", methods=["GET"])
def _get_step(network_index, route_index, step_index):
    global _networks
    return jsonify(_networks[network_index].routes[route_index].steps[step_index].serialize())


@app.route("/networks/<int:network_index>/routes/<int:route_index>/sections/<int:section_index>/", methods=["GET"])
def _get_section(network_index, route_index, section_index):
    global _networks
    return jsonify(_networks[network_index].routes[route_index].sections[section_index].serialize())
