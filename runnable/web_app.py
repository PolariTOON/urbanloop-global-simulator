import logging
import os
from json import dumps
from threading import Thread

from flask import Flask, Response, redirect, url_for

from model import loop
from model import sim_record
from model import station
from model import switch
from settings import json_serializer
from settings import network
from simulator import sim_loop
from sys import path

web_directory = os.path.abspath('%s/../resources/web' % (path[0]))
app = Flask(__name__, static_folder=web_directory, template_folder=web_directory)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
sim_thread = None
last_record = None
is_network_loaded = False
is_simulation_started = False
update_get_count = 0


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/load')  # TODO Add file parameter
def load_network():
    global is_network_loaded
    if not is_network_loaded:
        is_network_loaded = True
        network.load(web=True)
    return redirect(url_for('root'))


@app.route('/start')
def start_simulation():
    global sim_thread
    global is_simulation_started
    if not is_simulation_started:
        is_simulation_started = True
        sim_thread = Thread(target=sim_loop.run_simulation, args=(None, True))
        sim_thread.start()
    return redirect(url_for('root'))


@app.route('/time.json')
def generate_time_json():
    if sim_record.is_empty():
        return Response(mimetype="application/json")
    global update_get_count
    update_get_count += 1
    update_record()
    return Response(dumps(last_record.time_record), mimetype="application/json")


@app.route('/loops.json')
def generate_loops_json():
    list_loop_json = [json_serializer.serialize_loop(a_loop) for a_loop in loop.get_loops()]
    return Response(dumps(list_loop_json), mimetype="application/json")


@app.route('/stationsSetData.json')
def generate_stations_set_data_json():
    list_stations_set_data_json = [json_serializer.serialize_station_set_data(a_station) for a_station in
                                   station.get_stations()]
    return Response(dumps(list_stations_set_data_json), mimetype="application/json")


@app.route('/switchesSetData.json')
def generate_switches_set_data_json():
    list_switches_set_data_json = [json_serializer.serialize_switch_set_data(a_switch) for a_switch in
                                   switch.get_switches()]
    return Response(dumps(list_switches_set_data_json), mimetype="application/json")


@app.route('/stationsVarData.json')
def generate_stations_var_data_json():
    if sim_record.is_empty():
        return Response(mimetype="application/json")

    list_stations_var_data_json = [json_serializer.serialize_station_var_data(a_station) for a_station in
                                   last_record.stations_record]
    return Response(dumps(list_stations_var_data_json), mimetype="application/json")


@app.route('/switchesVarData.json')
def generate_switches_var_data_json():
    if sim_record.is_empty():
        return Response(mimetype="application/json")

    list_switches_var_data_json = [json_serializer.serialize_switch_var_data(a_switch) for a_switch in
                                   last_record.switches_record]
    return Response(dumps(list_switches_var_data_json), mimetype="application/json")


@app.route('/capsules.json')
def generate_capsules_json():
    if sim_record.is_empty():
        return Response(mimetype="application/json")
    global update_get_count
    update_get_count += 1
    update_record()

    list_capsules_json = last_record.capsules_record
    return Response(dumps(list_capsules_json), mimetype="application/json")


def update_record():
    global last_record
    global update_get_count

    if last_record is None or update_get_count == 2:
        update_get_count = 0
        last_record = sim_record.get_record()


if __name__ == '__main__':
    logging.info("http://127.0.0.1:8090")
    app.run(port=8090)

