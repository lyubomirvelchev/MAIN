from PyQt5 import QtWidgets

from UI.common import CommonSection
from UI.filter_section.filter_section import FilterSingleGroup
from UI.indicator_section.indicator_section import SingleIndicator
from UI.table_section.table_section import TickerTable
from filters.daily_downloader import get_ticker_types


class CentralWidget(QtWidgets.QWidget):
    def __init__(self, ticker_types):
        super(CentralWidget, self).__init__()
        self.central_layout = QtWidgets.QVBoxLayout()
        self.central_layout.addWidget(CommonSection(FilterSingleGroup, rows_arguments={"ticker_types": ticker_types,
                                                                                       "label": 'Filters:'
                                                                                       }))
        self.central_layout.addWidget(CommonSection(SingleIndicator, rows_arguments={"label": 'Indicators:'}))
        self.setLayout(self.central_layout)

        self.test_btn = QtWidgets.QPushButton('test')
        self.central_layout.addWidget(self.test_btn)

        self.ticker_table = TickerTable()
        # self.central_layout.addWidget(self.ticker_table)\
        self.ticker_table.show()

        self.test_btn.clicked.connect(self.ticker_table.set_table)


class MainUI(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainUI, self).__init__(*args, **kwargs)
        self.ticker_types = get_ticker_types()
        self.setup_ui()

    def setup_ui(self):
        self.central = CentralWidget(self.ticker_types)
        self.setCentralWidget(self.central)
