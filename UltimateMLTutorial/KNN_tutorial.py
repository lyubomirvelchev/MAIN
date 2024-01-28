import os
import time
import warnings

import numpy as np
import pandas as pd
from sklearn import neighbors, metrics
from sklearn.model_selection import train_test_split
from KNN_mappings import *

warnings.filterwarnings("ignore")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
car_data_path = os.path.join(ROOT_DIR, 'datasets', 'car.data')

car_data = pd.read_csv(car_data_path)

X = car_data[['buying', 'maint', 'safety', 'doors', 'persons', 'lug_boot']]
y = car_data[['class']]

# converting the strings to numbers

X['buying'] = X['buying'].map(vhigh_mapping)
X['maint'] = X['maint'].map(vhigh_mapping)
X['doors'] = X['doors'].map(doors_mapping)
X['persons'] = X['persons'].map(persons_mapping)
X['lug_boot'] = X['lug_boot'].map(lug_boot_mapping)
X['safety'] = X['safety'].map(vhigh_mapping)
y['class'] = y['class'].map(label_mapping)
y = np.array(y)


def execute_knn_ml(n, train_percent, weights, X=X, y=y):
    knn = neighbors.KNeighborsClassifier(n_neighbors=n, weights=weights)

    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=train_percent)
    knn.fit(X_train, y_train)

    predictions = knn.predict(X_test)

    accuracy = metrics.accuracy_score(y_test, predictions)
    return accuracy


def test_different_params(iterations, n, test_size, weights):
    start_time = time.time()
    sum = 0
    for _ in range(iterations):
        sum += execute_knn_ml(n, test_size, weights)
    return round(sum / iterations, 5), round(time.time() - start_time, 5)


if __name__ == '__main__':
    print(test_different_params(5000, 22, 0.7, 'uniform'))
    print(test_different_params(5000, 25, 0.7, 'uniform'))
    print(test_different_params(5000, 28, 0.7, 'uniform'))
    print(test_different_params(5000, 31, 0.7, 'uniform'))
    print("------")
    print(test_different_params(5000, 22, 0.75, 'uniform'))
    print(test_different_params(5000, 25, 0.75, 'uniform'))
    print(test_different_params(5000, 28, 0.75, 'uniform'))
    print(test_different_params(5000, 31, 0.75, 'uniform'))
    print("------")
    print(test_different_params(5000, 22, 0.8, 'uniform'))
    print(test_different_params(5000, 25, 0.8, 'uniform'))
    print(test_different_params(5000, 28, 0.8, 'uniform'))
    print(test_different_params(5000, 31, 0.8, 'uniform'))
    print("------")
