import numpy as np

# generate 100000 elements in a list numbers between 0 and 100 using

numbers = np.random.normal(50, 3, 100000).round().astype(int)
# remove all elements smaller than 0 and bigger than 100
numbers = [i for i in numbers if i >= 0 and i <= 100]


dictt = {
    '0-9': [i for i in numbers if i < 10],
    '10-19': [i for i in numbers if i < 20 and i >= 10],
    '20-29': [i for i in numbers if i < 30 and i >= 20],
    '30-39': [i for i in numbers if i < 40 and i >= 30],
    '40-49': [i for i in numbers if i < 50 and i >= 40],
    '50-59': [i for i in numbers if i < 60 and i >= 50],
    '60-69': [i for i in numbers if i < 70 and i >= 60],
    '70-79': [i for i in numbers if i < 80 and i >= 70],
    '80-89': [i for i in numbers if i < 90 and i >= 80],
    '90-99': [i for i in numbers if i < 100 and i >= 90],
}

# plot histogram with matplotlib

import matplotlib.pyplot as plt

plt.hist(numbers, bins=10)
plt.show()