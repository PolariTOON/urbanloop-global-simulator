"""
Classe qui est liée à une simulation
"""
from controler.routing import Routing


class Simulation:
    def __init__(self):
        self.controler = Routing()
        self.converter = Converter()
