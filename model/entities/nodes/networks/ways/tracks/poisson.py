from math import *
import random
import sys

def fact(n):
    """fact(n): calcule la factorielle de n (entier >= 0)"""
    x=1
    for i in range(2,n+1):
        x*=i
    return x

def lpoisson(k,m):
    """lpoisson(k,m): donne la probabilité d'avoir k évènements distribués selon une loi de Poisson de paramètre m"""
    return e**(-m)*m**k/fact(k)

def hpoisson(m):
    """Génération de valeurs tirées au hasard selon une distribution de Poisson pour la génération ds voyageurs"""
    ph=random.random()
    k=0
    pc=lpoisson(k,m)
    while ph>pc:
        k+=1
        pc+=lpoisson(k,m)
    return k 