import logging
import os
from json import dumps
from sys import path

from flask import Flask, Response, redirect, url_for

from model import loop, station, switch, warehouse, capsule
from settings import json_serializer, network, stoppable_thread as sth
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


@app.route('/load')  # TODO Add file parameter
def load_network():
    global is_network_loaded
    if not is_network_loaded:
        is_network_loaded = True
        network.load()
    return redirect(url_for('root'))


@app.route('/start')
def start_simulation():
    global sim_thread
    global is_simulation_started
    if not is_simulation_started:
        is_simulation_started = True
        sim_thread = sth.StoppableThread(target=sim_loop.run_simulation, args=(None, True))
        sim_thread.start()

    return redirect(url_for('root'))


@app.route('/stop')
def stop_simulation():
    global is_simulation_started, sim_thread
    is_simulation_started = False
    # stops simulation
    sim_thread.stop()
    del sim_thread

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


if __name__ == '__main__':
    # logging.info("http://127.0.0.1:8090")
    print("http://127.0.0.1:8090")
    app.run(port=8090)
