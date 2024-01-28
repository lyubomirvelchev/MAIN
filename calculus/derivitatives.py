import matplotlib.pyplot as plt
import numpy as np


def f(x):
    return x ** 2


array = np.linspace(0, 10, 2000)


def derivitatives(x):
    return 2 * x


plt.plot(array, derivitatives(array), 'b')
plt.plot(array, f(array), 'r')
plt.show()
