import matplotlib.pyplot as plt
import numpy as np
import scipy.stats

x_left = np.linspace(0, 12, 43200)
x_right = np.linspace(12, 24, 43200)
x_all = np.linspace(0, 24, 86400)

plt.plot(x_all, np.zeros(86400), 'b', label='Neutral')
plt.plot(x_all, 40 * np.ones(86400), 'c', label='City')
plt.plot(x_left, 30 + 50 * scipy.stats.norm.pdf(x_left, 8, 1), 'y')
plt.plot(x_left, 30 - 50 * scipy.stats.norm.pdf(x_left, 8, 1), 'g')
plt.plot(x_right, 30 + 50 * scipy.stats.norm.pdf(x_right, 18, 1), 'g', label='Residential')
plt.plot(x_right, 30 - 50 * scipy.stats.norm.pdf(x_right, 18, 1), 'y', label='Activity')


plt.grid()
plt.legend(loc='best')
plt.xlim(0, 24)
plt.ylim(0, 60)
plt.show()
