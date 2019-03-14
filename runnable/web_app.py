import logging
import os
from json import dumps, loads
from sys import path
from threading import Thread

from flask import Flask, Response, redirect, url_for, request

from model import loop, station, switch, warehouse, capsule
from settings import config
from settings import json_serializer, network
from simulator import sim_loop

web_directory = os.path.abspath('%s/../resources/web' % (path[0]))
app = Flask(__name__, static_folder=web_directory, template_folder=web_directory)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
sim_thread = None
is_network_loaded = False
is_simulation_started = False


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/load.json')  # TODO Add file parameter
def load_network():
    global is_network_loaded
    if not is_network_loaded:
        is_network_loaded = True
        network.reload()
    return Response(dumps(json_serializer.serialize_network()), mimetype="application/json")


@app.route('/start')
def start_simulation():
    global sim_thread
    global is_simulation_started
    if not is_simulation_started:
        is_simulation_started = True
        sim_thread = Thread(target=sim_loop.start_simulation, args=[True])
        sim_thread.start()
    return redirect(url_for('root'))


@app.route('/pause')
def pause_simulation():
    if is_simulation_started and not sim_loop.is_paused():
        sim_loop.pause_simulation()
    return redirect(url_for('root'))


@app.route('/resume')
def resume_simulation():
    if is_simulation_started and sim_loop.is_paused():
        sim_loop.run_simulation_after_pause()
    return redirect(url_for('root'))


@app.route('/stop')
def stop_simulation():
    global is_simulation_started
    global is_network_loaded
    if is_simulation_started:
        is_simulation_started = False
        is_network_loaded = False
        sim_loop.stop_simulation()
    return redirect(url_for('root'))


@app.route('/end-signal')
def end_signal():
    return Response(dumps({'endSignal': sim_loop.get_off_signal(reset=True)}), mimetype="application/json")


@app.route('/accelerate')
def accelerate_simulation():
    if is_simulation_started:
        sim_loop.accelerate_simulation()
    return redirect(url_for('root'))


@app.route('/decelerate')
def decelerate_simulation():
    if is_simulation_started:
        sim_loop.decelerate_simulation()
    return redirect(url_for('root'))


@app.route('/time.json')
def generate_time_json():
    return Response(dumps(json_serializer.serialize_time()), mimetype="application/json")


@app.route('/loops.json')
def generate_loops_json():
    return Response(dumps([json_serializer.serialize_loop(a_loop) for a_loop in loop.get_loops()]),
                    mimetype="application/json")


@app.route('/stationsSetData.json')
def generate_stations_set_data_json():
    return Response(dumps([json_serializer.serialize_station_set_data(a_station) for a_station in
                           station.get_stations()]), mimetype="application/json")


@app.route('/warehousesSetData.json')
def generate_warehouses_set_data_json():
    return Response(dumps([json_serializer.serialize_warehouse_set_data(a_warehouse) for a_warehouse in
                           warehouse.get_warehouses()]), mimetype="application/json")


@app.route('/switchesSetData.json')
def generate_switches_set_data_json():
    return Response(dumps([json_serializer.serialize_switch_set_data(a_switch) for a_switch in
                           switch.get_switches()]), mimetype="application/json")


@app.route('/stationsVarData.json')
def generate_stations_var_data_json():
    return Response(dumps([json_serializer.serialize_station_var_data(a_station) for a_station in
                           station.get_stations()]), mimetype="application/json")


@app.route('/warehousesVarData.json')
def generate_warehouses_var_data_json():
    return Response(dumps([json_serializer.serialize_warehouse_var_data(a_warehouse) for a_warehouse in
                           warehouse.get_warehouses()]), mimetype="application/json")


@app.route('/switchesVarData.json')
def generate_switches_var_data_json():
    return Response(dumps([]), mimetype="application/json")


@app.route('/capsules.json')
def generate_capsules_json():
    return Response(dumps([json_serializer.serialize_capsule(a_capsule) for a_capsule in capsule.get_capsules()]),
                    mimetype="application/json")


@app.route('/config.json/<int:permanent>', methods=['GET', 'POST'])
def load_config(permanent):
    if request.method == 'POST':
        config.modify(loads(request.form['data']), (True, False)[permanent is None or permanent == 0])
        config.load_editable()
    return Response(dumps(json_serializer.serialize_config()), mimetype="application/json")


@app.route('/reset-config')
def reset_config():
    config.reset()
    config.load_default()
    return redirect(url_for('root'))


if __name__ == '__main__':
    print("http://127.0.0.1:8090")
    app.run(port=8090)
