import configparser
import sys

"""
 ce fichier permets l'import des différentes valeurs et paramètre du fichier resources/config.ini
 
https://docs.python.org/dev/library/configparser.html
"""

loaded = False
default = None
interface = None
model = None
capsule = None
routing = None
sim = None


def load(file_name):
    global loaded
    global default
    global model
    global sim
    global interface
    global capsule
    global routing
    loaded = True
    config = configparser.ConfigParser()
    config.read(file_name)
    default = config['DEFAULT']
    interface = config['INTERFACE']
    model = config['MODEL']
    capsule = config['CAPSULE']
    routing = config['ROUTING']
    sim = config['SIM']


if loaded is False:
    load('{0}/../resources/config.ini'.format(sys.path[0]))
