import configparser

default = None
interface = None
model = None
capsule = None
routing = None
sim = None


def load(file_name):
    global default
    global model
    global sim
    global interface
    global capsule
    global routing
    config = configparser.ConfigParser()
    config.read(file_name)
    default = config['DEFAULT']
    interface = config['INTERFACE']
    model = config['MODEL']
    capsule = config['CAPSULE']
    routing = config['ROUTING']
    sim = config['SIM']


