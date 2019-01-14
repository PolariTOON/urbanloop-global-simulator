import numpy as np


class Poisson:
    def __init__(self):
        """45000 voyageurs par jour"""
        self.traveler_per_day = 45000
        self.peak_hours_coefficient = [1, 1, 1, 1, 2, 3, 3, 6, 8, 8, 7, 4, 5, 5, 4, 4, 6, 7, 8, 6, 4, 3, 2, 2]
        self.lambda_per_hour = [(self.traveler_per_day * phc) / (3600 * np.sum(self.peak_hours_coefficient)) for phc
                                in self.peak_hours_coefficient]

    def generate(self, hour):
        return np.random.poisson(self.lambda_per_hour[hour], 1)[0]
