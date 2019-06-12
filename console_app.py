"""
Cette classe permet de gérer le code lié à un lancement d'une simulation sans interface graphique
"""
from time import time
from model import routing, switch
from settings import config, network, simlog
from simulator import converter, sim_loop


def run_app():
    START_TIME = time()
    config.restore_config()
    routing.init_routing()
    switch.init_switch()
    converter.init_converter()
    simlog.load()
    network.load()
    simlog.debug("Simulation starts")
    sim_loop.start_simulation()
    simlog.debug("Execution time : %.3f seconds" % (time() - START_TIME))
    simlog.debug("Simulation time : %.1f seconds" % (sim_loop.get_simulated_time()))
