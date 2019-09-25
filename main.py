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


def tick(value):
    tick = float(value)
    if 0 < tick and isfinite(tick):
        return tick
    raise ArgumentTypeError("%s is not a valid tick" % value)


argument_parser = ArgumentParser(description="Run the UrbanLoop simulator")
argument_parser.add_argument("-n", "--networks", type=networks, default="{}", help="open the given networks or none by default")
argument_parser.add_argument("-p", "--port", type=port, default=-1, const=8090, nargs='?', help="run a web application on the given port or 8090 by default")
argument_parser.add_argument("-t", "--tick", type=tick, default=.042, help="set the tick to the given duration (in seconds) or .042 by default")
arguments = argument_parser.parse_args()

if arguments.port is -1:
    from console_app import run_app
    run_app(arguments.networks, arguments.tick)
else:
    from web_app import run_app
    run_app(arguments.port, arguments.networks, arguments.tick)
