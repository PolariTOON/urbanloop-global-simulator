""" classe permettant de lancer les pages webs des simulations"""

from time import sleep
from threading import Thread
import webbrowser
import sys


class Simulations(Thread):
    def __init__(self, port, number):
        self.port = port
        self.number = number
        Thread.__init__(self)

    def run(self):
        sleep(5) #pour laisser la simulation commencer avant d'ouvrir la page
        for i in range(0, self.number):
            id = i
            webbrowser.open_new_tab('http://127.0.0.1:%s/?id=%s' %(self.port, id))


if __name__ == '__main__':
    simulations = Simulations(int(sys.argv[1]), int(sys.argv[2]))
    simulations.run()
