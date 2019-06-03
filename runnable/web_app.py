import logging
import os
from json import dumps, loads
from sys import path
from threading import Thread

from flask import Flask, Response, redirect, url_for, request

from model import loop, station, switch, warehouse, capsule
from settings import config, network, json_serializer, simlog
from simulator import sim_loop

web_directory = os.path.abspath('%s/../resources/web' % (path[0]))
app = Flask(__name__, static_folder=web_directory, template_folder=web_directory)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
sim_thread = None
is_simulation_started = False


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/start', methods=['POST'])
def start_simulation():
    global sim_thread
    global is_simulation_started
    if not is_simulation_started:
        network.init_capsules()
        is_simulation_started = True
        sim_thread = Thread(target=sim_loop.start_simulation, args=[True])
        sim_thread.start()
    return redirect(url_for('root'))


@app.route('/stop', methods=['POST'])
def stop_simulation():
    global is_simulation_started
    if is_simulation_started:
        is_simulation_started = False
        sim_loop.stop_simulation()
    return redirect(url_for('root'))


@app.route('/pause', methods=['POST'])
def pause_simulation():
    if is_simulation_started and not sim_loop.is_paused():
        sim_loop.pause_simulation()
    return redirect(url_for('root'))


@app.route('/resume', methods=['POST'])
def resume_simulation():
    if is_simulation_started and sim_loop.is_paused():
        sim_loop.run_simulation_after_pause()
    return redirect(url_for('root'))


@app.route('/accelerate', methods=['POST'])
def accelerate_simulation():
    if is_simulation_started:
        sim_loop.accelerate_simulation()
    return redirect(url_for('root'))


@app.route('/decelerate', methods=['POST'])
def decelerate_simulation():
    if is_simulation_started:
        sim_loop.decelerate_simulation()
    return redirect(url_for('root'))


@app.route('/time.json', methods=['GET'])
def generate_time_json():
    return Response(dumps(json_serializer.serialize_time()), mimetype="application/json")


@app.route('/load.json/', methods=['GET'], defaults={'file_name': None})
@app.route('/load.json/<string:file_name>', methods=['GET'])
def load_network(file_name):
    if not is_simulation_started:
        if file_name is not None:
            network.reload(file_name=file_name, capsules_fulfill=False)
        else:
            network.reload(capsules_fulfill=False)
    return Response(dumps(json_serializer.serialize_network_size()), mimetype="application/json")


@app.route('/loops.json', methods=['GET'])
def generate_loops_json():
    return Response(dumps([json_serializer.serialize_loop(a_loop) for a_loop in loop.get_loops()]),
                    mimetype="application/json")


@app.route('/stationsSetData.json', methods=['GET'])
def generate_stations_set_data_json():
    return Response(dumps([json_serializer.serialize_station_set_data(a_station) for a_station in
                           station.get_stations()]), mimetype="application/json")


@app.route('/warehousesSetData.json', methods=['GET'])
def generate_warehouses_set_data_json():
    return Response(dumps([json_serializer.serialize_warehouse_set_data(a_warehouse) for a_warehouse in
                           warehouse.get_warehouses()]), mimetype="application/json")


@app.route('/switchesSetData.json', methods=['GET'])
def generate_switches_set_data_json():
    return Response(dumps([json_serializer.serialize_switch_set_data(a_switch) for a_switch in
                           switch.get_switches()]), mimetype="application/json")


@app.route('/updatedData.json', methods=['GET'])
def generate_updated_data_json():
    list_time_data = [json_serializer.serialize_time()]
    list_station_var_data = [json_serializer.serialize_station_var_data(a_station) for a_station in
                             station.get_stations()]
    list_warehouse_var_data = [json_serializer.serialize_warehouse_var_data(a_warehouse) for a_warehouse in
                               warehouse.get_warehouses()]
    list_switch_var_data = []

    list_capsule_data = [json_serializer.serialize_capsule(a_capsule) for a_capsule in capsule.get_capsules()]

    return Response(dumps(list_time_data +
                          list_station_var_data +
                          list_warehouse_var_data +
                          list_switch_var_data +
                          list_capsule_data), mimetype="application/json")


@app.route('/network-files.json', methods=['GET'])
def network_files():
    default_name = 'default: ' + network.get_default_file_name()
    network_file_names = [json_serializer.serialize_network_file_name(default_name)] + \
                         [json_serializer.serialize_network_file_name(network_file_name) for network_file_name in
                          network.get_network_file_names()]
    return Response(dumps(network_file_names), mimetype="application/json")


@app.route('/add-network-file/<string:file_name>', methods=['POST'])
def add_network_file(file_name):
    network.add_network_file(file_name, loads(request.form['data']))
    return redirect(url_for('root'))


@app.route('/dl-network-file.json/<string:file_name>/<int:is_default>', methods=['POST'])
def dl_network_file(file_name, is_default):
    return Response(dumps(network.get_network_json(file_name, (True, False)[is_default is None or is_default == 0])),
                    mimetype="application/json")


@app.route('/remove-network-file/<string:file_name>', methods=['POST'])
def remove_network_file(file_name):
    network.remove_network_file(file_name)
    return redirect(url_for('root'))


@app.route('/change-default-network-file/<string:file_name>', methods=['POST'])
def change_default_network_file(file_name):
    network.change_default_file(file_name)
    return redirect(url_for('root'))


@app.route('/change-config/<int:permanent>', methods=['POST'])
def change_config(permanent):
    config.modify(loads(request.form['data']), (True, False)[permanent is None or permanent == 0])
    config.load_editable()
    simlog.load()
    return redirect(url_for('root'))


@app.route('/reset-config', methods=['POST'])
def reset_config():
    config.reset_to_default()
    config.load_default()
    simlog.load()
    return redirect(url_for('root'))


@app.route('/config.json/<int:permanent>', methods=['GET'])
def load_config(permanent):
    return Response(dumps(json_serializer.serialize_config()), mimetype="application/json")


if __name__ == '__main__':
    print("http://127.0.0.1:8090")
    app.run(port=8090)
