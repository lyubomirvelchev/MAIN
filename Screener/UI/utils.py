from PyQt5 import QtWidgets


def delete_nested(w):
    if isinstance(w, QtWidgets.QWidget):
        w.deleteLater()
        w.setParent(None)
        del w
    else:
        cw = w.widget()
        if cw is not None:
            cw.deleteLater()
            cw.setParent(None)
            del cw
        else:
            try:
                at = w.takeAt(0)
                while at is not None:
                    delete_nested(at)
                    at = w.takeAt(0)
                w.setParent(None)
                w.deleteLater()
                del w
            except AttributeError:
                pass


class MementoMixin:
    def get_memento(self):
        return {}

    def set_memento(self, memo):
        pass



