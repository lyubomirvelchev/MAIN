import sys
import multiprocessing
from UI.window import MainUI, MainApplication

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = MainApplication(sys.argv)
    windows = MainUI()
    windows.setGeometry(400, 100, 500, 500)
    windows.show()
    sys.exit(app.exec_())
