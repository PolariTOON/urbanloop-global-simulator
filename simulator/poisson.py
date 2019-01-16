import numpy as np

from settings import config


class Poisson:
    def __init__(self):
        self.peak_hours_coefficient = [1, 1, 1, 1, 2, 3, 3, 6, 8, 8, 7, 4, 5, 5, 4, 4, 6, 7, 8, 6, 4, 3, 2, 2]
        self.traveller_lambda_per_hour = [
            (int(config.default['traveler_per_day']) * coefficient) / (3600 * np.sum(self.peak_hours_coefficient))
            for coefficient in self.peak_hours_coefficient]
        self.defect_lambda = int(config.default['defect_per_day']) / 86400

    def traveler(self, hour):
        return np.random.poisson(self.traveller_lambda_per_hour[hour], 1)[0]

    def defect(self):
        return np.random.poisson(self.defect_lambda, 1)[0]
