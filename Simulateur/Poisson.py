import numpy as np
import math as m

class Poisson:
    def __init__(self):
        """45000 voyageurs par jour donc 0.54 par seconde"""
        self.lambd = 0.54

    def generate(self):
        result = np.random.poisson(self.lambd, 1)
        return m.floor(np.mean(result))
