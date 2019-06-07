import logging
from threading import Thread

from flask import Flask, request, jsonify
from flask.json import loads

from model import loop, station, switch, warehouse, capsule, sensor
from settings import config, network, simlog
from simulator import sim_loop, converter

web_directory = 'resources/web'
app = Flask(__name__, static_folder=web_directory, template_folder=web_directory)
app.logger.setLevel(logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.ERROR)
sim_thread = None


@app.errorhandler(Exception)
def send_error(error):
    global app
    app.logger.error(error)
    return '', 404


@app.route('/')
def root():
    global app
    return app.send_static_file('index.html')


@app.route('/time.json', methods=['GET'])
def generate_time_json():
    return jsonify(converter.serialize_clock())


@app.route('/start', methods=['POST'])
def start_simulation():
    global sim_thread
    if sim_thread is None:
        network.init_capsules()
        sim_thread = Thread(target=sim_loop.start_simulation, args=[True])
        sim_thread.start()
    return ''


@app.route('/stop', methods=['POST'])
def stop_simulation():
    global sim_thread
    if sim_thread is not None:
        sim_thread = None
        sim_loop.stop_simulation()
    return ''


@app.route('/pause', methods=['POST'])
def pause_simulation():
    global sim_thread
    if sim_thread is not None and not sim_loop.is_paused():
        sim_loop.pause_simulation()
    return ''


@app.route('/resume', methods=['POST'])
def resume_simulation():
    global sim_thread
    if sim_thread is not None and sim_loop.is_paused():
        sim_loop.run_simulation_after_pause()
    return ''


@app.route('/accelerate', methods=['POST'])
def accelerate_simulation():
    global sim_thread
    if sim_thread is not None:
        sim_loop.accelerate_simulation()
    return ''


@app.route('/decelerate', methods=['POST'])
def decelerate_simulation():
    global sim_thread
    if sim_thread is not None:
        sim_loop.decelerate_simulation()
    return ''


@app.route('/loops.json', methods=['GET'])
def generate_loops_json():
    return jsonify([a_loop.serialize() for a_loop in loop.get_loops()])


@app.route('/stationsSetData.json', methods=['GET'])
def generate_stations_set_data_json():
    return jsonify([a_station.serialize() for a_station in station.get_stations()])


@app.route('/warehousesSetData.json', methods=['GET'])
def generate_warehouses_set_data_json():
    return jsonify([a_warehouse.serialize() for a_warehouse in warehouse.get_warehouses()])


@app.route('/switchesSetData.json', methods=['GET'])
def generate_switches_set_data_json():
    return jsonify([a_switch.serialize() for a_switch in switch.get_switches()])


@app.route('/sensorSetData.json', methods=['GET'])
def generate_sensors_set_data_json():
    return jsonify([a_sensor.serialize() for a_sensor in sensor.get_sensors()])


@app.route('/updatedData.json', methods=['GET'])
def generate_updated_data_json():
    list_clock_data = [converter.serialize_clock()]
    list_station_var_data = [a_station.serialize() for a_station in station.get_stations()]
    list_warehouse_var_data = [a_warehouse.serialize() for a_warehouse in warehouse.get_warehouses()]
    list_switch_var_data = [a_switch.serialize() for a_switch in switch.get_switches()]
    list_capsule_data = [a_capsule.serialize() for a_capsule in capsule.get_capsules()]
    list_sensor_data = [a_sensor.serialize() for a_sensor in sensor.get_sensors()]
    return jsonify(
        list_clock_data + list_station_var_data + list_warehouse_var_data + list_switch_var_data + list_capsule_data + list_sensor_data)


@app.route('/network-files.json', methods=['GET'])
def network_files():
    default_name = 'default: ' + network.get_default_file_name()
    network_file_names = [network.serialize_network_file_name(default_name)] + [
        network.serialize_network_file_name(network_file_name) for network_file_name in
        network.get_network_file_names()]
    return jsonify(network_file_names)


# TODO: change default getter
@app.route('/dl-network-file.json/<string:file_name>/<int:is_default>', methods=['POST'])
def dl_network_file(file_name, is_default):
    return jsonify(network.get_network_json(file_name, (True, False)[is_default is None or is_default == 0]))


# TODO: change default loader
@app.route('/load.json/', methods=['GET'], defaults={'file_name': None})
@app.route('/load.json/<string:file_name>', methods=['GET'])
def load_network(file_name):
    global sim_thread
    if sim_thread is None:
        if file_name is not None:
            network.reload(file_name=file_name, capsules_fulfill=False)
        else:
            network.reload(capsules_fulfill=False)
    return jsonify(network.serialize_network_size())


@app.route('/add-network-file/<string:file_name>', methods=['POST'])
def add_network_file(file_name):
    network.add_network_file(file_name, loads(request.form['data']))
    return ''


@app.route('/remove-network-file/<string:file_name>', methods=['POST'])
def remove_network_file(file_name):
    network.remove_network_file(file_name)
    return ''


@app.route('/change-default-network-file/<string:file_name>', methods=['POST'])
def change_default_network_file(file_name):
    network.change_default_file(file_name)
    return ''


@app.route('/change-config/<int:permanent>', methods=['POST'])
def change_config(permanent):
    config.modify(loads(request.form['data']), (True, False)[permanent is None or permanent == 0])
    config.load_editable()
    simlog.load()
    return ''


@app.route('/reset-config', methods=['POST'])
def reset_config():
    config.reset_to_default()
    config.load_default()
    simlog.load()
    return ''


@app.route('/config.json/<int:permanent>', methods=['GET'])
def load_config(permanent):
    return jsonify(config.serialize_config())
