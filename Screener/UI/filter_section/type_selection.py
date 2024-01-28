from PyQt5 import QtWidgets

from UI.utils import MementoMixin


class LabelAndCheckbox(QtWidgets.QHBoxLayout, MementoMixin):
    def __init__(self, text, *args, **kwargs):
        super(LabelAndCheckbox, self).__init__(*args, **kwargs)
        self.text = text
        self.setup_UI()

    def setup_UI(self):
        self.checkbox = QtWidgets.QCheckBox()
        self.addWidget(QtWidgets.QLabel(self.text))
        self.addStretch()
        self.addWidget(self.checkbox)

    def get_memento(self):
        return {self.text: self.checkbox.isChecked()}

    def set_memento(self, memo):
        self.checkbox.setChecked(memo)


class TypeSelectionWindow(QtWidgets.QMainWindow, MementoMixin):
    def __init__(self, ticker_types, *args, **kwargs):
        super(TypeSelectionWindow, self).__init__(*args, **kwargs)
        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)
        self.ticker_types = ticker_types
        self.inverse_ticker_types = {value: key for key, value in self.ticker_types.items()}

        self.setup_UI()

    def setup_UI(self):
        self.vlayout = QtWidgets.QVBoxLayout()
        for ticker_type in self.ticker_types:
            self.vlayout.addLayout(LabelAndCheckbox(ticker_type))
        self.main_widget.setLayout(self.vlayout)

    def get_children_memo(self):
        return [ch.get_memento() for ch in self.vlayout.children()]

    def get_memento(self):
        ts = []
        for t in self.get_children_memo():
            name, activated = list(t.items())[0]
            if activated:
                ts.append(self.ticker_types[name])

        return ts

    def set_memento(self, memo):
        types_to_set = []
        for ttype in memo:
            types_to_set.append(self.inverse_ticker_types[ttype])
        for ch in self.vlayout.children():
            if ch.text in types_to_set:
                ch.set_memento(True)