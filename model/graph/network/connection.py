"""
Gestion de la jonction/connexion entre :
    * une route et un bridge
    * un bridge et une route
    * une route et une route
"""

from .network_arc import NetworkArc


class Connection(NetworkArc):
    def __init__(self):
        pass

    def serialize(self):
        return super().serialize().update({
            'jsonType': 'connection'
        })
