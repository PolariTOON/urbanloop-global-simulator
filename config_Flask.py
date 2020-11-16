from asyncio import run, run_coroutine_threadsafe, sleep
from flask import Flask, jsonify, request
from functools import wraps
from logging import ERROR, getLogger
from controler.simulation import Simulation
import modifjson

"""Classe chargée de la réalisation de la simulation avec interface web"""

_app = Flask(__name__, static_url_path="", static_folder="view/static", template_folder="view/templates")
_app.logger.setLevel(ERROR)
getLogger("werkzeug").setLevel(ERROR)

_running_default = False    # par défaut on ne lance pas les simulations
_speed_default = 0          # par défaut la vitesse de simulation est x1

def _synchronize(key=None):
    """Synchronisation du serveur flask avec simpy, NE PAS TOUCHER"""
    if not isinstance(key, str):
        key = None
    def synchronize(coroutine):
        @wraps(coroutine)
        def routine(*args, **kwargs):
            if key is not None:
                kwargs[key] = request.get_json()
            from app import _loop, _simulations
            future = run_coroutine_threadsafe(coroutine(_simulations, *args, **kwargs), _loop)
            exception = future.exception()
            if exception is not None:
                result = None
                print("\u001b[31m", exception, "\u001b[0m")
            else:
                result = future.result()
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
    """ Requête post pour envoyer et charger un réseau depuis la vue à partir d'un fichier json
        network_item contient toutes les informations du fichier JSON
    """
    if network_item is not None:
        network_item = modifjson.mod_station(network_item) # ajout des mini-boucles pour dépots et stations si besoin
        if "id" in network_item:
            del network_item["id"]
        from app import _wave, _remove_travelers
        simulation = Simulation(network_index, _wave, remove_travelers=_remove_travelers, **network_item)

        # Pour utiliser la simulation dans l'API
        print("Creation simulation en tant que variable global (pour utiliser dans l'API)")
        global simulation_for_api  # Variable non locale a cette fonction
        # Je ne sais pas pk declarer en dehors de cette fonction "simulation_for_api = None" ne marche pas, cela ne change la valeur de la var que localement ...
        simulation_for_api = simulation

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



@_app.route("/networks/<int:network_index>/travelersWaiting/show/", methods=["POST"])
@_synchronize()
async def _show_travelers_waiting(simulations, network_index):
    """Requête post pour afficher le nombre de passagers attendant dans les stations depuis la vue"""
    if network_index in simulations:
        simulation = simulations[network_index]
        simulation.showing_travelers_waiting = True
        return True
    return False

@_app.route("/networks/<int:network_index>/travelersWaiting/hide/", methods=["POST"])
@_synchronize()
async def _hide_travelers_waiting(simulations, network_index):
    """Requête post pour afficher le nombre de passagers attendant dans les stations depuis la vue"""
    if network_index in simulations:
        simulation = simulations[network_index]
        simulation.showing_travelers_waiting = False
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


@_app.route("/networks/<int:network_index>/roads/<int:road_index>/", methods=["GET"])
@_synchronize()
async def _get_road(simulations, network_index, road_index):
    """Requête get pour récupérer le fichier json d'une route depuis la vue"""
    return simulations[network_index]._network.roads[road_index].serialize()


@_app.route("/networks/<int:network_index>/roads/<int:road_index>/steps/<int:step_index>/", methods=["GET"])
@_synchronize()
async def _get_step(simulations, network_index, road_index, step_index):
    """Requête get pour récupérer le fichier json d'une étape depuis la vue"""
    return simulations[network_index]._network.roads[road_index].steps[step_index].serialize()


@_app.route("/networks/<int:network_index>/roads/<int:road_index>/sections/<int:section_index>/", methods=["GET"])
@_synchronize()
async def _get_section(simulations, network_index, road_index, section_index):
    """Requête get pour récupérer le fichier json d'une section depuis la vue"""
    return simulations[network_index]._network.roads[road_index].sections[section_index].serialize()


@_app.route("/networks/<int:network_index>/close/<section_name>/", methods=["POST"])
@_synchronize()
async def _close(simulations, network_index, section_name):
    """Requête post pour fermer une section depuis la vue"""
    if network_index in simulations:
        simulation = simulations[network_index]
        network = simulation.get_network()
        for road in network.roads:
            for section in road.sections:
                if section.name == section_name:
                    section.fermeture_ouverture()
        network._update_routing()  # mise à jour des tables de routage
        return True
    return False


def run_app(port, networks, wave):
    """Fonction permettant de lancer l'application"""
    "port = n° de port si on souhaite l'interface web (sinon -1)"
    "networks contient les réseaux préchargés"
    "wave contient la vitesse de tic de simulation"

    print("App running on port %d (http://127.0.0.1:%d)" % (port, port))
    _app.run(host="0.0.0.0", port=port)



###############################################
# RESTFUL API FLASK POUR APPLIS MOBILE


# INFOS D'UNE CAPSULE
@_app.route('/capsule/<int:user_id>/', methods=['GET'])
def getUserPosition(user_id):
    """ Donne les infos de la capsule dont on a renseigne l'identifiant     A DEVELOPPER"""

    try:
        simulation_for_api
    except NameError:
        return jsonify({ 'msg': 'La simulation n\'a pas ete chargee -_-' })

    pod_of_user = simulation_for_api.get_network().get_pod_of_user(user_id)

    if (pod_of_user == None):
        return jsonify({ 'status_user': "En attente d'une capsule ou capsule non trouvee"})
    else :
        #print(pod_of_user.getPreviousStation())
        return jsonify({ 'source': pod_of_user.source,
                         'next_station': pod_of_user.getNextStation(),
                         'destination': pod_of_user.destination,
                         'time_before_arrival': pod_of_user.getTimeBeforeArrival()})



# CREATION NOUVEAU TRAJET DANS SIMULATEUR
@_app.route('/new_trip', methods=['POST'])
def add_trip():
    """Fonction permettant de donner un nouveau trajet au simulateur"""

    try:
        simulation_for_api
    except NameError:
        return jsonify({ 'msg': 'La simulation n\'a pas ete chargee' })

    user_id = request.json['user_id']
    departure = request.json['departure']
    arrival = request.json['arrival']
    #typeCapsule = request.json['typeCapsule']

    #Lien infos recues-simulateur
    simulation_for_api.add_traveler(departure, arrival, user_id)

    return jsonify({ 'msg': 'Trajet valide' })

#Argument : 
#{
    #"user_id": "1321",
    #"departure": "TNCY",
    #"arrival": "commanderie"
    #"typeCapsule" : "solo"
#}
