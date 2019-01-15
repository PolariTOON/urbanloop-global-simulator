from simulator import poisson


class DefectGenerator:
    def __init__(self, env):
        self.env = env
        self.poisson = poisson.Poisson()

    def generate_defect(self):
        # TODO
        print("TODO")
