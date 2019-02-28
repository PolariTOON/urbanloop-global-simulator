import os
from json import dumps
from threading import Thread

from flask import Flask, Response, redirect, url_for

from model import capsule
from model import loop
from model import station
from model import switch
from settings import json_serializer
from settings import network
from simulator import sim_loop

web_directory = os.path.abspath('../resources/web')
app = Flask(__name__, static_folder=web_directory, template_folder=web_directory)
sim_thread = None


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/load')  # TODO Add file parameter
def load_network():
    network.load(web=True)
    return redirect(url_for('root'))


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


@app.route('/capsules.json')
def generate_capsules_json():
    list_capsules_json = [json_serializer.serialize_capsule(a_capsule) for a_capsule in
                          capsule.get_capsules()]
    return Response(dumps(list_capsules_json), mimetype="application/json")


@app.route('/start')
def start():
    global sim_thread
    network.load()
    sim_thread = Thread(target=sim_loop.run_simulation)
    sim_thread.start()
    return redirect(url_for('root'))


if __name__ == '__main__':
    app.run(port=8090)
