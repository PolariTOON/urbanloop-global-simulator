"""
Type de noeud du sous-graphe du réseau qui représente un garage où sont stocker des capsules
"""

from .step import Step


class Warehouse(Step):
    def __init__(self):
        super().__init__(self)

    def serialize():
        return super().serialize().update({
            'type': 'warehouse'
        })
