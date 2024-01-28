from sklearn import datasets
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn import metrics

iris = datasets.load_iris()

X = iris.data
y = iris.target
classes = ['Iris Setosa', 'Iris Versicolour', 'Iris Virginica']
train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.2)
model = svm.SVC()
model.fit(train_X, train_y)

predictions = model.predict(test_X)

acc = metrics.accuracy_score(test_y, predictions)

print(predictions)
print(test_y)
print(acc)
