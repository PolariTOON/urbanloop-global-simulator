from enum import Enum
from settings import config
from simulator import flow_generator


class SimState(Enum):
    RUNNING = 0
    SLEEP = 1
    KILLED = 2


class SimLoop:
    def __init__(self, env, sim_tick):
        self.env = env
        self.sim_tick = sim_tick
        self.sim_state = SimState.RUNNING
        self.flow_generator = flow_generator.FlowGenerator(env)
        self.start_hour = int(config.sim['start_hour'])

    def loop(self):
        while True:
            if self.sim_state == SimState.RUNNING:
                yield self.env.process(self.flow_generator.generate_traveler(
                    env=self.env,
                    sim_tick=self.sim_tick,
                    start_hour=self.start_hour)
                )
            elif self.sim_state == SimState.SLEEP:
                print("SLEEP State")
            elif self.sim_state == SimState.KILLED:
                yield self.env.exit()
