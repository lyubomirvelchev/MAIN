import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import pandas as pd


class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])


class TickerTable(QtWidgets.QTableView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data = pd.DataFrame([
            [1, 9, 2],
            [1, 0, -1],
            [3, 5, 2],
            [3, 3, 2],
            [5, 8, 9],
        ], columns=['A', 'B', 'C'], index=['Row 1', 'Row 2', 'Row 3', 'Row 4', 'Row 5'])

        self.setModel(TableModel(self.data))

    def set_table(self):
        self.data['A']['Row 1']= 123
        self.setModel(TableModel(self.data))

