from sklearn import datasets
import numpy as np
from sklearn.model_selection import train_test_split

iris = datasets.load_iris()

X = iris.data
y = iris.target

train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.2)
