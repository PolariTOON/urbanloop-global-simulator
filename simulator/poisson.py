import numpy as np
from settings import config


class Poisson:
    def __init__(self):
        self.traveler_per_day = int(config.default['traveler_per_day'])
        self.peak_hours_coefficient = [1, 1, 1, 1, 2, 3, 3, 6, 8, 8, 7, 4, 5, 5, 4, 4, 6, 7, 8, 6, 4, 3, 2, 2]
        self.lambda_per_hour = [(self.traveler_per_day * coefficient) / (3600 * np.sum(self.peak_hours_coefficient)) for coefficient
                                in self.peak_hours_coefficient]

    def generate(self, hour):
        return np.random.poisson(self.lambda_per_hour[hour], 1)[0]
