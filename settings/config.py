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

path = 'resources/config.ini'
default_path = 'resources/default_config.ini'


def reset_config():
    """
    Replace all the values in the config.ini file with default values
    """
    copyfile(default_path, path)
    restore_config()


def save_config(config_json):
    """
    This function overwrites a new config under a json format and saves it
    into resources/config.ini
    :param config_json: A json with exact same value of attributes
    """
    for line in fileinput.input(path, inplace=True):
        output = line
        for attribute, value in config_json.items():
            if attribute in line and '#' not in line:
                output = line.split('=')[0].lstrip().rstrip() + '=' + str(value) + '\n'
                break
        sys.stdout.write(output)
    restore_config()


def restore_config():
    """
    This function loads the resources/config.ini config file.
    """
    global loaded
    global traveler
    global topology
    global prob
    global capsule
    global routing
    global sim
    config = configparser.ConfigParser()
    config.read(path)
    traveler = config['TRAVELER']
    topology = config['TOPOLOGY']
    prob = config['PROB']
    capsule = config['CAPSULE']
    routing = config['ROUTING']
    sim = config['SIM']
    loaded = True


def serialize_config():
    if loaded is False:
        return None
    return {
        'travelers_per_day': int(traveler['travelers_per_day']),
        'trip_limit': int(traveler['trip_limit']),
        'traveler_limit': int(traveler['traveler_limit']),
        'ascent_descent_duration': int(traveler['ascent_descent_duration']),
        'morning_peak_hour': int(traveler['morning_peak_hour']),
        'evening_peak_hour': int(traveler['evening_peak_hour']),
        'network_file': topology['network_file'],
        'activity_and_residential_percent': int(prob['activity_and_residential_percent']),
        'city_percent': int(prob['city_percent']),
        'activity_and_residential_fluctuation': int(prob['activity_and_residential_fluctuation']),
        'max_speed': float(capsule['max_speed']),
        'number_of_capsules': int(capsule['number_of_capsules']),
        'station_refill': capsule['station_refill'],
        'fulfill_period': int(capsule['fulfill_period']),
        'switched_cost': int(routing['switched_cost']),
        'my_timer': int(routing['my_timer']),
        'timer_other': int(routing['timer_other']),
        'real_time': sim['real_time'],
        'endless': sim['endless'],
        'duration': int(sim['duration']),
        'start_hour': int(sim['start_hour']),
        'logs': sim['logs']
    }
