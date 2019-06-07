from argparse import ArgumentParser, ArgumentTypeError


def port(value):
    integer = int(value)
    if 0 <= integer < 65536:
        return integer
    raise ArgumentTypeError("%s is not a valid port" % value)


argument_parser = ArgumentParser(description="Run the UrbanLoop simulator")
argument_parser.add_argument("-p", "--port", type=port, default=-1, const=8090, nargs='?', help="run a web application on the given port or 8090 by default")
arguments = argument_parser.parse_args()


if arguments.port is -1:
    from time import time
    from model import routing, switch
    from settings import config, network, simlog
    from simulator import converter, sim_loop
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
else:
    from web_app import app
    print("http://127.0.0.1:%d" % arguments.port)
    app.run(port=arguments.port)
