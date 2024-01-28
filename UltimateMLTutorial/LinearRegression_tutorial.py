from sklearn import datasets
from sklearn import linear_model
from sklearn import metrics
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import warnings



def lin_reg_second_way(boston_data):
    X = boston_data.data
    y = boston_data.target

    df_x = pd.DataFrame(X, columns=boston_data.feature_names)
    df_y = pd.DataFrame(y)

    linear_regression = linear_model.LinearRegression()

    X_train, X_test, y_train, y_test = train_test_split(df_x, df_y, test_size=0.2, random_state=4)

    model = linear_regression.fit(X_train, y_train)

    print(linear_regression.coef_)

    a = linear_regression.predict(X_test)

    b=0

    #MEAN SQUARE ERROR
    print(np.mean((a-y_test)**2))


def lin_reg_first_way(boston_data):
    # plt.scatter(X.T[5], y)
    # plt.show()

    X = boston_data.data
    y = boston_data.target
    linear_regression = linear_model.LinearRegression()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = linear_regression.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print("predictions:", predictions)
    print("R^2:", linear_regression.score(X, y))
    print("coeficent:", linear_regression.coef_)
    print("intercept:", linear_regression.intercept_)


if __name__ == "__main__":
    warnings.filterwarnings("ignore")

    boston_data = datasets.load_boston()

    lin_reg_first_way(boston_data)
    lin_reg_second_way(boston_data)
