from asyncio import run, run_coroutine_threadsafe, sleep
from flask import Flask, jsonify, request, Response
from functools import wraps
from logging import ERROR, getLogger
from controler.simulation import Simulation

""" Fonctions chargées de la réalisation de la simulation avec interface web """

_app = Flask(__name__, static_url_path="", static_folder="view/static", template_folder="view/templates")
_app.logger.setLevel(ERROR)
getLogger("werkzeug").setLevel(ERROR)

_simulation_for_api = None
_running_default = False    # par défaut on ne lance pas les simulations
_speed_default = 0          # par défaut la vitesse de simulation est x1

def shutdown():
    """
        Permet de fermer l'application si :
            - les simulations sont terminées
            ou
            - un signal CTRL-C a été reçu
        ATTENTION :
        Cette méthode ne sera appelée que lors du traitement d'une requête HTTP.
        Si le programme est lancé avec l'interface web, le serveur ne sera donc
        jamais fermé tant qu'aucun client web ne fera de requête au serveur.
    """
    func = request.environ.get('werkzeug.server.shutdown')
    func()

def _synchronize(key=None):
    """ Synchronisation du serveur flask avec le thread des simulations, NE PAS TOUCHER """
    if not isinstance(key, str):
        key = None
    def synchronize(coroutine):
        @wraps(coroutine)
        def routine(*args, **kwargs):
            # check if the app was closed
            from app import _quit
            if _quit:
                shutdown()
                return jsonify(None)
            # else, handle request
            if key is not None:
                kwargs[key] = request.get_json()
            from app import _loop, _simulations
            #p_tb C'est durant cet appel que se produit l'erreur lors du rechargement d'un json
            #p_tb L'erreur est dans network.py, à _get_elt_of_loop()
            #p_tb print(f"args = {args}\n")
            #p_tb print(f"kwargs = {kwargs}\n")
            future = run_coroutine_threadsafe(coroutine(_simulations, *args, **kwargs), _loop)
            exception = future.exception()
            if exception is not None:
                result = None
                print("Error with: " + key)
                print("\u001b[31m", exception, "\u001b[0m")
            else:
                result = future.result()
            #try:
            #    return jsonify(result)
            #except Exception: raise ValueError(f"{result} non jsonifiable")
            #print("-----------------------------------------------------")
            #print("config_Flask : synchronize, print(result) (résultat du dico à donner à jsonify)")
            #print("")
            #print(result)
            #print("")
            #print("-----------------------------------------------------")
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

@_app.route("/<string:filename>.js")
def return_javascript(filename):
    """ javascript modules need to be sent with MIME type of : text/javascript
        this function ensures that javascript files are sent with the right MIME type.
    """
    js_filename = './view/static/' + filename + '.js'
    with open(js_filename, 'r') as f:
        content = f.read()
    return Response(response=content, mimetype="text/javascript")

@_app.route("/networks/<int:network_index>/", methods=["POST"])
@_synchronize("network_item")
async def _post_network(simulations, network_index, network_item):
    """ Requête POST pour envoyer et charger un réseau depuis la vue à partir d'un fichier json.
        network_item contient toutes les informations du fichier JSON
    """
    global _simulation_for_api
    if network_item is not None:
        from app import _wave, _remove_travelers
        if "id" in network_item:
            del network_item["id"]
        print("Received network: '%s'" % network_item["name"])
        simulation = Simulation(network_index, _wave, remove_travelers=_remove_travelers, **network_item)
        simulations[network_index] = simulation
        # Pour utiliser la simulation dans l'API
        _simulation_for_api = simulation
        return simulation.serialize()
    else:
        if network_index in simulations:
            del simulations[network_index]
        _simulation_for_api = None
        return None

@_app.route("/networks/<int:network_index>/", methods=["GET"])
@_synchronize()
async def _get_network(simulations, network_index):
    """ Requête GET pour récupérer le fichier json d'un réseau depuis la vue """
    if network_index in simulations:
        simulation = simulations[network_index]
        return simulation.serialize()
    return None


@_app.route("/networks/<int:network_index>/clock/play/", methods=["POST"])
@_synchronize()
async def _play_clock(simulations, network_index):
    """ Requête POST pour lancer la simulation depuis la vue """
    if network_index in simulations:
        simulation = simulations[network_index]
        simulation.running = True
        return True
    return False


@_app.route("/networks/<int:network_index>/clock/pause/", methods=["POST"])
@_synchronize()
async def _pause_clock(simulations, network_index):
    """ Requête POST pour mettre en pause la simulation depuis la vue """
    if network_index in simulations:
        simulation = simulations[network_index]
        simulation.running = False
        return True
    return False



@_app.route("/networks/<int:network_index>/travelersWaiting/show/", methods=["POST"])
@_synchronize()
async def _show_travelers_waiting(simulations, network_index):
    """ Requête POST pour afficher le nombre de passagers attendant dans les stations depuis la vue """
    if network_index in simulations:
        simulation = simulations[network_index]
        simulation.showing_travelers_waiting = True
        return True
    return False

@_app.route("/networks/<int:network_index>/travelersWaiting/hide/", methods=["POST"])
@_synchronize()
async def _hide_travelers_waiting(simulations, network_index):
    """ Requête POST pour afficher le nombre de passagers attendant dans les stations depuis la vue """
    if network_index in simulations:
        simulation = simulations[network_index]
        simulation.showing_travelers_waiting = False
        return True
    return False



@_app.route("/networks/<int:network_index>/clock/decelerate/", methods=["POST"])
@_synchronize()
async def _decelerate_clock(simulations, network_index):
    """ Requête POST pour décélérer la simulation depuis la vue """
    if network_index in simulations:
        simulation = simulations[network_index]
        simulation.rate -= 1
        return True
    return False


@_app.route("/networks/<int:network_index>/clock/accelerate/", methods=["POST"])
@_synchronize()
async def _accelerate_clock(simulations, network_index):
    """ Requête POST pour accélérer la simulation depuis la vue """
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
    """ Requête GET pour récupérer le fichier json d'une boucle depuis la vue """
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



##########################################################################
# RESTFUL FLASK API pour les applications mobile et les bornes de stations


@_app.route('/capsule/<string:user_id>', methods=['GET'])
def get_user_position(user_id):
    """ Donne les infos de la capsule dont on a renseigne l'identifiant """

    global _simulation_for_api
    if _simulation_for_api == None:
        return jsonify({ 'msg': 'Aucune simulation n\'a pas été chargée' })

    pod_of_user = _simulation_for_api.get_network().get_pod_of_user(user_id)

    if (pod_of_user == None):
        return jsonify({ 'status_user': "En attente d'une capsule ou capsule non trouvee"})
    else :
        return jsonify({ 'source': pod_of_user.source,
                         'next_station': pod_of_user.get_next_station(),
                         'previous_station': pod_of_user.get_previous_station(),
                         'destination': pod_of_user.destination,
                         'time_before_arrival': pod_of_user.get_time_before_arrival()})


@_app.route('/new_trip', methods=['POST'])
def add_trip():
    """ Fonction permettant de donner un nouveau trajet au simulateur

    Argument du POST : 
        {
            "user_id": "1321",
            "departure": "Stanislas",
            "arrival": "Telecom Nancy",
            "typeCapsule" : "solo"
        }
    
    """

    global _simulation_for_api
    if _simulation_for_api == None:
        return jsonify({ 'msg': 'Aucune simulation n\'a pas été chargée' })
    
    user_id = request.json['user_id']
    departure = request.json['departure']
    arrival = request.json['arrival']
    #typeCapsule = request.json['typeCapsule']

    #Lien infos reçues-simulateur
    _simulation_for_api.add_traveler(departure, arrival, user_id)

    return jsonify({ 'msg': 'Trajet valide' })


@_app.route('/change_dest', methods=['POST'])
def change_destination_of_trip():
    """ Fonction permettant de changer de destination pour un utilisateur

    Argument du POST : 
        {
            "user_id": "1321",
            "new_arrival": "Velodrome"
        }
    
    """

    global _simulation_for_api
    if _simulation_for_api == None:
        return jsonify({ 'msg': 'Aucune simulation n\'a pas été chargée' })

    user_id = request.json['user_id']
    new_arrival = request.json['new_arrival']
    
    network = _simulation_for_api.get_network()
    pod_of_user = network.get_pod_of_user(user_id)

    if (pod_of_user == None):
        return jsonify({ 'status_user': "En attente d'une capsule ou capsule non trouvee"})
    else :
        network.pod_change_from_one_destination_to_another(pod_of_user.destination, new_arrival)
        pod_of_user.change_destination(user_id, new_arrival)
        return jsonify({ 'msg': 'Changement de destination valide' })


@_app.route('/emergency_exit/<string:user_id>', methods=['GET'])
def call_emergency_exit(user_id):
    """ Fonction permettant de demander une sortie d'urgence pour un utilisateur """

    global _simulation_for_api
    if _simulation_for_api == None:
        return jsonify({ 'msg': 'Aucune simulation n\'a pas été chargée' })

    network = _simulation_for_api.get_network()
    pod_of_user = network.get_pod_of_user(user_id)

    if (pod_of_user == None):
        return jsonify({ 'status_user': "En attente d'une capsule ou capsule non trouvee"})
    else :
        new_dest = pod_of_user.get_next_station()
        network.pod_change_from_one_destination_to_another(pod_of_user.destination, new_dest)
        pod_of_user.call_emergency_exit(user_id)
        return jsonify({ 'msg': 'Appel d\'urgence demande' })


#p_tbtc
@_app.route('/envoi_lavage/<string:user_id>', methods=['POST'])
def demander_envoi_au_lavage(user_id):
    """ Fonction permettant de demander l'envoi d'une capsule au lavage après le voyage, par l'utilisateur qui est dedans """

    global _simulation_for_api
    if _simulation_for_api == None:
        return jsonify({ 'msg': 'Aucune simulation n\'a été chargée' })

    network = _simulation_for_api.get_network()
    pod_of_user = network.get_pod_of_user(user_id)

    if (pod_of_user == None):
        return jsonify({ 'status_user': "En attente d'une capsule ou capsule non trouvee"})
    else :
        pod_of_user.demander_envoi_lavage(user_id)
        pod_of_user.dernier_signalement_lavage_par_vrai_utilisateur = True
        return jsonify({ 'msg': 'Demande d\'envoi au lavage faite' })


#p_tbtc
@_app.route('/capsule_lavage/<string:pod_id>', methods=['POST'])
def demander_revision_capsule(pod_id):
    """Fonction permettant de demander l'envoi d'une capsule au lavage après le voyage, par son pod_id"""

    global _simulation_for_api

    if _simulation_for_api is None:
        return jsonify({"msg": "Aucune simulation n'a été chargée"})
    else:

        network = _simulation_for_api.get_network()
        pod = network.get_pod_of_id(int(pod_id))
        print("***")
        print(pod.id if pod is not None else None)
        print("***")

        if pod is None:
            return jsonify({"status_user": "Capsule non trouvée"})
        else:
            pod.demander_envoi_lavage(None)
            pod.dernier_signalement_lavage_par_vrai_utilisateur = True
            return jsonify({"msg": f"Demande d'envoi au lavage pour la capsule {pod_id} faite"})


#p_tbtc
@_app.route('/capsule_revision/<string:pod_id>', methods=['POST'])
def demander_lavage_capsule(pod_id):
    """Fonction permettant de demander l'envoi d'une capsule à la révision après le voyage, par son pod_id"""

    global _simulation_for_api

    if _simulation_for_api is None:
        return jsonify({"msg": "Aucune simulation n'a été chargée"})
    else:

        network = _simulation_for_api.get_network()
        pod = network.get_pod_of_id(int(pod_id))
        print("***")
        print(pod.id if pod is not None else None)
        print("***")

        if pod is None:
            return jsonify({"status_user": "Capsule non trouvée"})
        else:
            pod.demander_envoi_revision(None)
            pod.dernier_signalement_revision_par_vrai_utilisateur = True
            return jsonify({"msg": f"Demande d'envoi à la révision pour la capsule {pod_id} faite"})


#p_tbtc
@_app.route('/envoi_revision/<string:user_id>', methods=['POST'])
def demander_envoi_en_revision(user_id):
    """ Fonction permettant de demander l'envoi d'une capsule en révision après le voyage, par l'utilisateur qui est dedans """

    global _simulation_for_api
    if _simulation_for_api == None:
        return jsonify({ 'msg': 'Aucune simulation n\'a été chargée' })

    network = _simulation_for_api.get_network()
    pod_of_user = network.get_pod_of_user(user_id)

    if (pod_of_user == None):
        return jsonify({ 'status_user': "En attente d'une capsule ou capsule non trouvee"})
    else :
        pod_of_user.demander_envoi_revision(user_id)
        pod_of_user.dernier_signalement_revision_par_vrai_utilisateur = True
        return jsonify({ 'msg': 'Demande d\'envoi en révision faite' })

