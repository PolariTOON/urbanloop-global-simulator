from argparse import ArgumentParser, ArgumentTypeError

from model.networks.network import Network
import json


def port(value):
    integer = int(value)
    if 0 <= integer < 65536:
        return integer
    raise ArgumentTypeError("%s is not a valid port" % value)


argument_parser = ArgumentParser(description="Run the UrbanLoop simulator")
argument_parser.add_argument("-p", "--port", type=port, default=-1, const=8090, nargs='?', help="run a web application on the given port or 8090 by default")
arguments = argument_parser.parse_args()


if arguments.port is -1:
    from console_app import run_app
    run_app()
elif arguments.port is 1:
    with open("resources/new_mini_network.json") as json_data:
        json_network = json.load(json_data)
    Network(**json_network)
else:
    from web_app import run_app
    run_app(arguments.port)
