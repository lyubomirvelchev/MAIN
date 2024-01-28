import inspect
import collections

from PyQt5 import QtWidgets, QtGui

from UI.row_cosntruction import RowFactory
from UI.utils import delete_nested, MementoMixin
import indicators as indicators_package
from screen.enum_data.enum_obj import ComparisonOperators
from indicators.indicators import FieldValueIndicator

INDICATORS = collections.OrderedDict(
    [(name, inspect.getfullargspec(cls.__init__))
     for name, cls in indicators_package.__dict__.items()
     if isinstance(cls, type)]
)


class IndicatorAlertRow(QtWidgets.QHBoxLayout, MementoMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_UI()
        self.setup_callbacks()

    def setup_UI(self):
        self.addSpacing(25)
        self.checkbox = QtWidgets.QCheckBox()
        self.addWidget(self.checkbox)

        self.operator_combobox = QtWidgets.QComboBox()
        self.operator_combobox.addItems(ComparisonOperators.__members__.keys())
        self.addWidget(self.operator_combobox)

        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setValidator(QtGui.QDoubleValidator(999999, -999999, 8))
        self.addWidget(self.line_edit)

        self.addStretch()

    def setup_callbacks(self):
        ...

    def is_selected(self):
        return self.checkbox.isChecked()

    def get_memento(self):
        memo = super().get_memento()

        memo.update({
            'operator': self.operator_combobox.currentIndex(),
            'value': self.line_edit.text()
        })

        return memo

    def set_memento(self, memo):
        self.operator_combobox.setCurrentIndex(memo['operator'])
        self.line_edit.setText(memo['value'])


class SingleIndicator(QtWidgets.QVBoxLayout, MementoMixin):
    def __init__(self, *args, row_args={}, **kwargs):
        super().__init__(*args, **kwargs)
        self.row_args = row_args
        self.setup_UI()
        self.setup_callbacks()

    def setup_UI(self):
        self.indicator_hbox = QtWidgets.QHBoxLayout()

        if not self.row_args.get('internal', False):

            self.checkbox = QtWidgets.QCheckBox()
            self.indicator_hbox.addWidget(self.checkbox)

            self.add_button = QtWidgets.QPushButton('+')
            self.add_button.setFixedSize(25, 25)
            self.indicator_hbox.addWidget(self.add_button)

            self.remove_button = QtWidgets.QPushButton('-')
            self.remove_button.setFixedSize(25, 25)
            self.indicator_hbox.addWidget(self.remove_button)
        else:
            self.indicator_hbox.addSpacing(25)

        self.indicator_dropbox = QtWidgets.QComboBox()

        self.indicator_dropbox.addItems([key for key in INDICATORS.keys()
                                         if not (key == 'STD' and self.row_args.get('internal', False))])
        self.indicator_hbox.addWidget(self.indicator_dropbox)

        self.addLayout(self.indicator_hbox)

        self.set_layout_slot()

        self.alerts = QtWidgets.QVBoxLayout()
        self.addLayout(self.alerts)

    def clear_slots(self):
        if hasattr(self, 'layout_slot'):
            delete_nested(self.layout_slot)
            del self.layout_slot
        if hasattr(self, 'layout_ref'):
            del self.layout_ref

        if hasattr(self, 'ind1'):
            delete_nested(self.ind1)
            del self.ind1

        if hasattr(self, 'ind2'):
            delete_nested(self.ind2)
            del self.ind2

    def set_layout_slot(self, *args, memo=None):
        self.clear_slots()

        selection = self.indicator_dropbox.currentText()
        if selection != 'STD':
            exclude = ['previous_data', 'current_minute']
            kwargs_defaults = dict(zip(INDICATORS[selection].args[::-1], INDICATORS[selection].defaults[::-1]))
            if kwargs_defaults.get('field', None) is not None:
                exclude.append('field')
            ags_names = INDICATORS[selection].args

            self.layout_slot, self.layout_ref = RowFactory(ags_names, exclude=exclude)
            if memo is not None:
                for name, wid in self.layout_ref.items():
                    if name in memo:
                        wid.set_memento(memo[name])
        else:
            self.layout_slot = QtWidgets.QHBoxLayout()
            self.ind1 = SingleIndicator(row_args={'internal': True})
            self.insertLayout(1, self.ind1)
            self.ind2 = SingleIndicator(row_args={'internal': True})
            self.insertLayout(2, self.ind2)
            if memo is not None:
                self.ind1.set_memento(memo['ind1'])
                self.ind2.set_memento(memo['ind2'])

        self.layout_slot.addStretch()
        self.indicator_hbox.addLayout(self.layout_slot)

    def add_alert(self, *args, **kwargs):
        self.alerts.addLayout(IndicatorAlertRow())

    def remove_alerts(self, *args, **kwargs):
        for ch in self.alerts.children():
            if ch.is_selected():
                delete_nested(ch)

    def set_alerts_memo(self, memo):
        self.remove_alerts()
        for alert_memo in memo:
            wdg = IndicatorAlertRow()
            wdg.set_memento(alert_memo)
            self.alerts.addLayout(wdg)

    def get_alerts_memento(self):
        return [ch.get_memento() for ch in self.alerts.children()]

    def setup_callbacks(self):
        self.indicator_dropbox.currentIndexChanged.connect(self.set_layout_slot)
        if not self.row_args.get('internal', False):
            self.add_button.clicked.connect(self.add_alert)
            self.remove_button.clicked.connect(self.remove_alerts)

    def remove_callbacks(self):
        self.indicator_dropbox.currentIndexChanged.disconnect()
        if not self.row_args.get('internal', False):
            self.add_button.clicked.disconnect()
            self.remove_button.clicked.disconnect()

    def is_selected(self):
        if not self.row_args.get('internal', False):
            return self.checkbox.isChecked()
        return False

    def get_arguments_memento(self):
        if hasattr(self, 'layout_ref'):
            return {name: wd.get_memento() for name, wd in self.layout_ref.items()}
        return {'ind1': self.ind1.get_memento(), 'ind2': self.ind2.get_memento()}

    def get_memento(self):
        memo = super().get_memento()
        memo.update({
            'indicator': self.indicator_dropbox.currentIndex(),
            'arguments': self.get_arguments_memento(),
        })
        alerts_memo = self.get_alerts_memento()
        if len(alerts_memo):
            memo.update({'alerts': alerts_memo})

        return memo

    def set_memento(self, memo):
        self.remove_callbacks()
        self.indicator_dropbox.setCurrentIndex(memo['indicator'])
        self.set_layout_slot(memo=memo['arguments'])
        if 'alerts' in memo:
            self.set_alerts_memo(memo['alerts'])
        self.setup_callbacks()
