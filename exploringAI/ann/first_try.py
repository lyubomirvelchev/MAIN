import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer
from sklearn.metrics import r2_score, mean_squared_error

PATH = 'data/50_Startups.csv'

dataset = pd.read_csv(PATH)
X, y = dataset.iloc[:, :-1].values, dataset.iloc[:, -1].values
X = ColumnTransformer([('encoder', OneHotEncoder(), [3])], remainder='passthrough').fit_transform(X)
X = X[:, 1:]
scaler = StandardScaler()
X[:, 2:] = scaler.fit_transform(X[:, 2:])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

regression_model = LinearRegression()
regression_model.fit(X_train, y_train)
regression_y_pred = regression_model.predict(X_test)

X_train = np.asarray(X_train).astype('float32')
y_train = np.asarray(y_train).astype('float32')
X_test = np.asarray(X_test).astype('float32')
y_test = np.asarray(y_test).astype('float32')
X = np.asarray(X).astype('float32')
y = np.asarray(y).astype('float32')

ann_model = tf.keras.models.Sequential([
    tf.keras.layers.Input(shape=(5,)),
    tf.keras.layers.Dense(units=64, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(units=48, activation='relu'),
    tf.keras.layers.Dense(units=32, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(units=16, activation='relu'),
    tf.keras.layers.Dense(units=1)
])

ann_model.compile(optimizer='adam',
                  loss='mse')

ann_model.fit(X_train, y_train, epochs=500, batch_size=1)
ann_y_pred = ann_model.predict(X_test)

print("Lin reg mse: ", round(mean_squared_error(regression_y_pred, y_test), 2))
print("Lin reg r2: ", round(r2_score(regression_y_pred, y_test), 4))
print("ANN mse: ", round(mean_squared_error(ann_y_pred, y_test), 2))
print("ANN r2: ", round(r2_score(ann_y_pred, y_test), 4))

plt.scatter(y_test, list(range(len(y_test))), color='red', label='Real')
plt.scatter(regression_y_pred, list(range(len(regression_y_pred))), color='blue', label='Lin reg', s=10)
plt.scatter(ann_y_pred, list(range(len(ann_y_pred))), color='black', label='ANN', s=10)
plt.legend()
plt.show()
