from PyQt5 import QtWidgets, QtGui

from UI.utils import MementoMixin
from screen.enum_data.enum_obj import DailyFields, ComparisonOperators, TimeFrames


def init_digit_line_edit(self, mask, *args, **kwargs):
    super(self.__class__, self).__init__(*args, **kwargs)
    self.setValidator(QtGui.QDoubleValidator(999999, -999999, 8))
    self.setInputMask(mask)


def get_memento_line_edit(self):
    return self.text()


def set_memento_line_edit(self, memo):
    super(self.__class__, self).set_memento(memo)
    self.setText(memo)


def init_combobox(self, entries, *args, **kwargs):
    super(self.__class__, self).__init__(*args, **kwargs)
    self.addItems(entries)


def get_memento_combobox(self):
    return self.currentIndex()


def set_memento_combobox(self, memo):
    super(self.__class__, self).set_memento(memo)
    self.setCurrentIndex(memo)


def init_checkbox(self, *args, **kwargs):
    super(self.__class__, self).__init__(*args, **kwargs)


def get_memento_checkbox(self):
    return self.isChecked()


def set_memento_checkbox(self, memo):
    self.setChecked(memo)


LINE_EDIT_FEATURES = {
    'classes': [QtWidgets.QLineEdit, MementoMixin],
    'methods': {
        '__init__': init_digit_line_edit,
        'get_memento': get_memento_line_edit,
        'set_memento': set_memento_line_edit
    }

}

COMBOBOX_FEATURES = {
    'classes': [QtWidgets.QComboBox, MementoMixin],
    'methods': {
        '__init__': init_combobox,
        'get_memento': get_memento_combobox,
        'set_memento': set_memento_combobox
    },
}

CHECKBOX_FEATURES = {
    'classes': [QtWidgets.QCheckBox, MementoMixin],
    'methods': {
        'get_memento': get_memento_checkbox,
        'set_memento': set_memento_checkbox
    },
}

WIDGET_TYPES = {
    'days_count': {**LINE_EDIT_FEATURES, 'args': ['000;']},
    'hour_count': {**LINE_EDIT_FEATURES, 'args': ['000;']},
    'win_size': {**LINE_EDIT_FEATURES, 'args': ['000;']},
    'percent': {**LINE_EDIT_FEATURES, 'args': ['#000.00;']},
    'value': {**LINE_EDIT_FEATURES, 'args': ['#000.00;']},

    'field': {**COMBOBOX_FEATURES, 'args': [list(DailyFields.__members__.keys()), ]},
    'compare_sign': {**COMBOBOX_FEATURES, 'args': [list(ComparisonOperators.__members__.keys()), ]},
    'time_frame': {**COMBOBOX_FEATURES, 'args': [list(TimeFrames.__members__.keys()), ]},

    'abs_value': CHECKBOX_FEATURES,
    'ignore_today_data': CHECKBOX_FEATURES,
    'pre_market': CHECKBOX_FEATURES,

}


class RowFactory:
    def __new__(cls, widget_names, *args, exclude=[], **kwargs):
        if 'self' not in exclude:
            exclude.append('self')

        layout = QtWidgets.QHBoxLayout()
        layout_ref = {}
        for name in widget_names:
            if name not in exclude:
                features = WIDGET_TYPES[name]

                layout.addWidget(QtWidgets.QLabel(' '.join(name.split('_'))))
                wid = type(name,
                           tuple(features['classes']),
                           features['methods'])(*features.get('args', []))
                layout.addWidget(wid)
                layout_ref[name] = wid

        layout.setContentsMargins(0, 0, 0, 0)

        return layout, layout_ref
