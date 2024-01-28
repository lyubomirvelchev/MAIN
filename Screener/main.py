import sys
from UI.аpplication import MainApplication
from UI.main_window import MainUI


if __name__ == "__main__":
    app = MainApplication(sys.argv)
    windows = MainUI()
    windows.show()
    sys.exit(app.exec_())