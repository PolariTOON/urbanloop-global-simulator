import matplotlib.pyplot as plt
import numpy as np

"""
Test pour approximer les courbes de probabilités
pour la direction des voyageurs.
Ce choix n'a pas été retenu
"""
lines = ""
try:
    with open('../resources/curves.txt', "r") as file:
        lines = file.readlines()
except FileNotFoundError:
    with open('resources/curves.txt', "r") as file:
        lines = file.readlines()

curves = []
for line in lines:
    curves.append([int(val.replace('\n', '')) for val in line.split(';')])

x_curve = np.linspace(0, 24, 24)
y_curve_down_up = np.array(curves[0])
y_curve_down_down = np.array(curves[1])

curve_down_up = np.poly1d(np.polyfit(x_curve, y_curve_down_up, 10))
curve_up_down = np.poly1d(np.polyfit(x_curve, y_curve_down_down, 10))

x_graph = np.linspace(0, 24, 86400)
plt.plot(x_graph, curve_down_up(x_graph), '--', x_graph, curve_up_down(x_graph), '--')
plt.ylim(0, 50)
plt.show()
