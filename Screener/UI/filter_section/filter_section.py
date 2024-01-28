from PyQt5 import QtWidgets, Qt

from UI.utils import MementoMixin, delete_nested
from UI.filter_section.type_selection import TypeSelectionWindow
from UI.row_cosntruction import RowFactory
from filters.filter_manager import FILTERS


class FilterSingleGroup(QtWidgets.QVBoxLayout, MementoMixin):
    def __init__(self, *args, row_args={}, **kwargs):
        super(FilterSingleGroup, self).__init__(*args, **kwargs)

        self.setup_UI()
        self.setup_additional_window(row_args['ticker_types'])
        self.setup_callbacks()

    def setup_UI(self):
        self.toolbar_hbox = QtWidgets.QHBoxLayout()

        self.checkbox = QtWidgets.QCheckBox()
        self.toolbar_hbox.addWidget(self.checkbox)

        self.title = QtWidgets.QTextEdit('Group')
        self.title.setSizePolicy(Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Fixed)
        self.title.setFixedSize(80, 25)

        self.toolbar_hbox.addWidget(self.title)

        self.add_button = QtWidgets.QPushButton('+')
        self.add_button.setFixedSize(25, 25)
        self.toolbar_hbox.addWidget(self.add_button)

        self.remove_button = QtWidgets.QPushButton('-')
        self.remove_button.setFixedSize(25, 25)
        self.toolbar_hbox.addWidget(self.remove_button)

        self.type_select_button = QtWidgets.QPushButton('Type')
        self.toolbar_hbox.addWidget(self.type_select_button)

        self.toolbar_hbox.addStretch()

        self.addLayout(self.toolbar_hbox)

        self.rows_section = QtWidgets.QHBoxLayout()
        self.rows_section.addSpacing(25)

        self.rows = QtWidgets.QVBoxLayout()
        self.rows_section.addLayout(self.rows)

        self.addLayout(self.rows_section)

    def setup_additional_window(self, ticker_types):
        self.type_window = TypeSelectionWindow(ticker_types=ticker_types)

    def setup_callbacks(self):
        self.add_button.clicked.connect(self.add_new_row)
        self.remove_button.clicked.connect(self.delete_selected_rows)
        self.type_select_button.clicked.connect(lambda *x, **y: self.type_window.show())

    def is_selected(self):
        return self.checkbox.isChecked()

    def add_new_row(self, *args, **kwargs):
        self.rows.addLayout(FilterSingleRow())

    def delete_selected_rows(self, *args, **kwargs):
        for_removal = []
        for idx, group in enumerate(self.rows.children()):
            if group.is_selected():
                for_removal.append(idx)

        for idx in for_removal[::-1]:
            w = self.rows.children()[idx]
            delete_nested(w)

    def delete_all_groups(self):
        for w in self.rows.children():
            delete_nested(w)

    def get_memento(self):
        memo = super(FilterSingleGroup, self).get_memento()
        memo.update({
            "group_filters": [fl.get_memento() for fl in self.rows.children()],
            "type_select": self.type_window.get_memento()

        })
        return memo

    def set_memento(self, memo):
        super(FilterSingleGroup, self).set_memento(memo)
        self.delete_all_groups()
        for fl in memo['group_filters']:
            row = FilterSingleRow()
            row.set_memento(fl)
            self.rows.addLayout(row)

        self.type_window.set_memento(memo['type_select'])


class FilterSingleRow(QtWidgets.QHBoxLayout, MementoMixin):
    def __init__(self, *args, row_args={}, **kwargs):
        super(FilterSingleRow, self).__init__(*args, **kwargs)
        self.setup_UI()
        self.setup_callbacks()

    def setup_UI(self):
        self.check_box = QtWidgets.QCheckBox()
        self.addWidget(self.check_box)

        self.time_interval_dropbox = QtWidgets.QComboBox()
        self.time_interval_dropbox.addItems(FILTERS.keys())
        self.addWidget(self.time_interval_dropbox)

        self.set_indicator_slot()

    def set_indicator_slot(self, *args, memo=None):
        if hasattr(self, 'indicator_slot'):
            delete_nested(self.indicator_slot)
        self.indicator_slot = FilterIndicatorSection(self.time_interval_dropbox.currentText())
        if memo:
            self.indicator_slot.set_memento(memo)
        self.addLayout(self.indicator_slot)

    def setup_callbacks(self):
        self.time_interval_dropbox.currentIndexChanged.connect(self.set_indicator_slot)

    def disable_callbacks(self):
        self.time_interval_dropbox.currentIndexChanged.disconnect()

    def get_memento(self):
        memo = super().get_memento()
        memo.update(
            {
                'time_interval': self.time_interval_dropbox.currentIndex(),
                'indicator_section': self.indicator_slot.get_memento()
            }

        )
        return memo

    def set_memento(self, memo):
        self.disable_callbacks()
        self.time_interval_dropbox.setCurrentIndex(memo['time_interval'])
        self.set_indicator_slot(memo=memo['indicator_section'])
        self.setup_callbacks()


class FilterIndicatorSection(QtWidgets.QHBoxLayout, MementoMixin):
    def __init__(self, time_interval):
        super().__init__()
        self.time_interval = time_interval
        self.setup_UI()
        self.setup_callbacks()

    def setup_UI(self):
        self.filter_combobox = QtWidgets.QComboBox()
        self.filter_combobox.addItems(FILTERS[self.time_interval].keys())
        self.addWidget(self.filter_combobox)
        self.setup_arguments()

    def setup_arguments(self,*args, memo=None):
        if hasattr(self, 'layout_slot'):
            delete_nested(self.layout_slot)
        ags_names = FILTERS[self.time_interval][self.filter_combobox.currentText()].args

        self.layout_slot, self.layout_ref = RowFactory(ags_names)
        self.layout_slot.addStretch()
        self.addLayout(self.layout_slot)
        if memo is not None:
            for wname, wobj in self.layout_ref.items():
                wobj.set_memento(memo[wname])

    def setup_callbacks(self):
        self.filter_combobox.currentIndexChanged.connect(self.setup_arguments)

    def stop_callbacks(self):
        self.filter_combobox.currentIndexChanged.disconnect()

    def get_memento(self):
        memo = super().get_memento()
        memo.update(
            {
                'filter':self.filter_combobox.currentIndex(),
                'arguments': {name: widget.get_memento() for name, widget in self.layout_ref.items()}
            }

        )
        return memo

    def set_memento(self, memo):
        self.stop_callbacks()
        self.filter_combobox.setCurrentIndex(memo['filter'])
        self.setup_arguments(memo=memo['arguments'])
        self.setup_callbacks()
