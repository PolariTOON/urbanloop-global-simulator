import numpy as np

from settings import config


class Poisson:
    def __init__(self):
        self.peak_hours_coefficient = [1, 1, 1, 1, 2, 3, 3, 6, 8, 8, 7, 4, 5, 5, 4, 4, 6, 7, 8, 6, 4, 3, 2, 2]
        self.traveller_lambda_per_hour = [
            (int(config.default['travelers_per_day']) * coefficient) / (3600 * np.sum(self.peak_hours_coefficient))
            for coefficient in self.peak_hours_coefficient]
        # self.defect_lambda = int(config.default['defect_per_day']) / 86400
        print(config.default['travelers_per_day'])

    def traveler(self, hour):
        """
        This function gives you the amount of travelers you would create
        at a given hour.
        The lambda parameter is calculated hour by hour. It represents
        the mean number of travelers in a second.
        :param hour: The hour at which you want to create a traveler
        :return: The number of traveler you would create at the given hour.
        """
        return np.random.poisson(self.traveller_lambda_per_hour[hour], 1)[0]

    def defect(self):
        """
        This function gives you the amount of defects you would create.
        The lambda parameter represents the mean number of defects in a second.
        :return: The number of traveler you would create.
        """
        return np.random.poisson(self.defect_lambda, 1)[0]
