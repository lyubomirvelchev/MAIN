from PyQt5 import QtWidgets
from UI.central_widget import CentralWidget


class MainApplication(QtWidgets.QApplication):
    pass


class MainUI(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainUI, self).__init__(*args, **kwargs)
        self.setup_ui()

    def setup_ui(self):
        self.central = CentralWidget()
        self.setCentralWidget(self.central)

    def closeEvent(self, a0):
        self.centralWidget().closeEvent(a0)
        super(MainUI, self).closeEvent(a0)
