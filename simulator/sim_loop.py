from simulator import flow_generator
from simulator import sim_state

START_HOUR = 20


class SimLoop:
    def __init__(self, env, sim_tick):
        self.env = env
        self.sim_tick = sim_tick
        self.sim_state = sim_state.SimState.RUNNING
        self.flow_generator = flow_generator.FlowGenerator(env)

    def loop(self):
        while True:
            if self.sim_state == sim_state.SimState.RUNNING:
                yield self.env.process(
                    self.flow_generator.generate_traveler(env=self.env, sim_tick=self.sim_tick, start_hour=START_HOUR))
            elif self.sim_state == sim_state.SimState.SLEEP:
                print("SLEEP State")
            elif self.sim_state == sim_state.SimState.KILLED:
                yield self.env.exit()
