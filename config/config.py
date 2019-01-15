import configparser

default = None
interface = None
model = None
sim = None


def load(file_name):
    global default
    global model
    global sim
    global interface
    config = configparser.ConfigParser()
    config.read(file_name)
    default = config['DEFAULT']
    interface = config['INTERFACE']
    model = config['MODEL']
    sim = config['SIM']


