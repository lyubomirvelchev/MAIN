from PyQt5 import QtWidgets, Qt
from UI.utils import MementoMixin, delete_nested
from UI.events import CallbackList


class ControlButtons(QtWidgets.QHBoxLayout):
    def __init__(self, *args, label='Groups:', **kwargs):
        super(ControlButtons, self).__init__(*args, **kwargs)
        self.label = label
        self.setup_UI()

    def setup_UI(self):
        self.buttons = {key: QtWidgets.QPushButton(key.capitalize())
                        for key in ['new', 'delete', 'cancel', 'apply']}
        self.addWidget(QtWidgets.QLabel(self.label))
        for button in self.buttons.values():
            self.addWidget(button)


class CommonSection(QtWidgets.QWidget, MementoMixin):
    def __init__(self, rows_widget, *args, rows_arguments={}, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows_widget = rows_widget
        self.rows_arguments = rows_arguments

        self.setup_UI()
        self.setup_callbacks()
        self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)

    def setup_UI(self):
        self.control_buttons = ControlButtons(label=self.rows_arguments.get('label'))
        self.content_rows = CommonRows(self.rows_widget, single_row_arguments=self.rows_arguments)
        box = QtWidgets.QVBoxLayout()
        box.addLayout(self.control_buttons)
        box.addWidget(self.content_rows)
        self.setLayout(box)

    def setup_callbacks(self):
        self.apply_callback = CallbackList()
        self.apply_callback.attach(self.content_rows.apply_changes)

        self.control_buttons.buttons['new'].clicked.connect(self.content_rows.add_new_group)
        self.control_buttons.buttons['apply'].clicked.connect(self.apply_callback)
        self.control_buttons.buttons['delete'].clicked.connect(self.content_rows.delete_selected_groups)
        self.control_buttons.buttons['cancel'].clicked.connect(self.content_rows.cancel_changes)

    def get_memento(self):
        return self.content_rows.get_memento()

    def set_memento(self, memo):
        super().set_memento(memo)
        self.content_rows.set_memento(memo)


class CommonRows(QtWidgets.QScrollArea, MementoMixin):
    def __init__(self, single_row_element, *args, single_row_arguments={}, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = []
        self.single_row_element = single_row_element
        self.single_row_arguments = single_row_arguments

        self.central_widget = QtWidgets.QWidget()
        self.central_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.setWidget(self.central_widget)
        self.setWidgetResizable(True)

    def add_new_group(self, *args, **kwargs):
        self.central_layout.addLayout(self.single_row_element(row_args=self.single_row_arguments))
        self.central_widget.resize(self.central_layout.sizeHint())

    def apply_changes(self, *args, **kwargs):
        self.state = self.get_children_memento()

    def cancel_changes(self, *args, **kwargs):
        self.delete_all_groups()
        if len(self.state):
            self.set_children_memento(self.state)

    def delete_selected_groups(self, *args, **kwargs):
        for_removal = []
        for idx, group in enumerate(self.central_layout.children()):
            if group.is_selected():
                for_removal.append(idx)

        for idx in for_removal[::-1]:
            w = self.central_layout.children()[idx]
            delete_nested(w)

    def delete_all_groups(self):
        for w in self.central_layout.children():
            delete_nested(w)

    def get_children_memento(self):
        return [ch.get_memento() for ch in self.central_layout.children()]

    def set_children_memento(self, state):
        for group_state in state:
            new_group = self.single_row_element(row_args=self.single_row_arguments)
            new_group.set_memento(group_state)
            self.central_layout.addLayout(new_group)

    def get_memento(self):
        memo = super().get_memento()
        memo.update({
            'contents': self.get_children_memento()
        })
        return memo

    def set_memento(self, memo):
        self.delete_all_groups()
        self.set_children_memento(memo['contents'])
