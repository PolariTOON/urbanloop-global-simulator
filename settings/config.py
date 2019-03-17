import configparser
import fileinput
import sys

from shutil import copyfile

"""
This file permits to import different values of the config files :
    - resources/default_config.ini
    - resources/config.ini
 
https://docs.python.org/dev/library/configparser.html
"""

loaded = False
modified = False
traveler = None
topology = None
prob = None
capsule = None
routing = None
sim = None
_loaded_signal = False

path = '{0}/../resources/config.ini'.format(sys.path[0])
default_path = '{0}/../resources/default_config.ini'.format(sys.path[0])


def load(file_name):
    global loaded
    global traveler
    global topology
    global prob
    global capsule
    global routing
    global sim
    global _loaded_signal
    config = configparser.ConfigParser()
    config.read(file_name)
    traveler = config['TRAVELER']
    topology = config['TOPOLOGY']
    prob = config['PROB']
    capsule = config['CAPSULE']
    routing = config['ROUTING']
    sim = config['SIM']
    if loaded:
        _loaded_signal = True
    loaded = True


def load_default():
    """
    This function loads the resources/default_config.ini config file.
    """
    load(default_path)


def load_editable():
    """
    This function loads the resources/config.ini config file.
    """
    load(path)


def modify(config_json, permanent=False):
    """
    This function overwrites a new config under a json format and saves it
    into resources/config.ini
    :param config_json: A json with exact same value of attributes
    :param permanent: If permanent is true, both default_config and config
    will be overwritten.
    """
    global modified

    modified_path = path
    if permanent:
        modified_path = default_path

    for line in fileinput.input(modified_path, inplace=True):
        output = line
        for attribute, value in config_json.items():
            if attribute in line and '#' not in line:
                output = line.split('=')[0].lstrip().rstrip() + '=' + str(value) + '\n'
                break
        sys.stdout.write(output)

    modified = True
    if permanent:
        modified = False
        modify(config_json, permanent=False)


def reset_to_default(force=False):
    """
    Replace all the values in the config.ini file with default values
    """
    global modified
    if modified or force:
        copyfile(default_path, path)
        modified = False


if loaded is False:
    reset_to_default(force=True)
    load_default()


def get_loaded_signal(reset=False):
    """
    :param reset: If reset, _modified_signal = False
    :return: Returns a boolean indicating that config modification has ended
    """
    global _loaded_signal
    if _loaded_signal and reset:
        _loaded_signal = False
        return True
    return _loaded_signal
