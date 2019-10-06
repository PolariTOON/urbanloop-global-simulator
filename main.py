from argparse import ArgumentParser, ArgumentTypeError
from json import loads
from math import isfinite


def networks(value):
    entries = loads(value)
    networks = {}
    for key in entries:
        index = int(key)
        item = str(entries[key])
        if 0 <= index:
            networks[index] = item
            continue
        raise ArgumentTypeError("%s is not a valid index" % key)
    return networks


def port(value):
    port = int(value)
    if 0 <= port < 65536:
        return port
    raise ArgumentTypeError("%s is not a valid port" % value)


def wave(value):
    wave = float(value)
    if 0 < wave and isfinite(wave):
        return wave
    raise ArgumentTypeError("%s is not a valid wave" % value)


argument_parser = ArgumentParser(description="Run the UrbanLoop simulator")
argument_parser.add_argument("-n", "--networks", type=networks, default="{}", help="load the given networks or none by default")
argument_parser.add_argument("-p", "--port", type=port, default=-1, const=8090, nargs='?', help="run a web application on the given port or 8090 by default")
argument_parser.add_argument("-w", "--wave", type=wave, default=.042, help="set the duration of each wave to the given value (in seconds) or .042 seconds by default")
arguments = argument_parser.parse_args()

if arguments.port is -1:
    from console_app import run_app
    run_app(arguments.networks, arguments.wave)
else:
    from web_app import run_app
    run_app(arguments.port, arguments.networks, arguments.wave)
