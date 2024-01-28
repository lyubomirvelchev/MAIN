import pickle
import os.path
import datetime

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
from project_constants import *
from UI.UI_utils import ArticlesProgressCounter, ArticleWorker


class CentralWidget(QtWidgets.QWidget):
    def __init__(self):
        super(CentralWidget, self).__init__()
        central_layout = self.set_central_widget_layout()
        self.setLayout(central_layout)

    def set_central_widget_layout(self):
        central_layout = QtWidgets.QVBoxLayout()
        query_layout = self.set_query_layout()
        central_layout.addLayout(query_layout)
        links_layout = self.set_links_layout()
        central_layout.addLayout(links_layout)
        save_file_layout = self.set_file_location_layout()
        central_layout.addLayout(save_file_layout)
        self.button = QtWidgets.QPushButton("Initiate Jihad!")
        central_layout.addWidget(self.button)
        self.error_log = self.set_error_log()
        central_layout.addWidget(self.error_log)
        self.progress_counter = ArticlesProgressCounter()
        central_layout.addWidget(self.progress_counter)
        self.button.clicked.connect(self.execute_scraping)
        self.set_memento()
        return central_layout

    def set_query_layout(self):
        self.label_1 = QtWidgets.QLabel('Query')
        self.query = QtWidgets.QLineEdit()
        self.label_2 = QtWidgets.QLabel('Number of links')
        self.number_links = QtWidgets.QLineEdit()
        query_layout = QtWidgets.QHBoxLayout()
        query_layout.addWidget(self.label_1)
        query_layout.addWidget(self.query)
        query_layout.addWidget(self.label_2)
        query_layout.addWidget(self.number_links)
        return query_layout

    def set_links_layout(self):
        self.links_label = QtWidgets.QLabel("Links")
        self.links_text_box = QtWidgets.QTextEdit()
        self.links_text_box.setMinimumSize(100, 100)
        self.links_text_box.setMaximumSize(400, 200)
        links_layout = QtWidgets.QHBoxLayout()
        links_layout.addWidget(self.links_label)
        links_layout.addWidget(self.links_text_box)
        return links_layout

    def set_file_location_layout(self):
        self.save_file_label = QtWidgets.QLabel('File Location')
        self.save_file_path = QtWidgets.QLineEdit()
        save_file_layout = QtWidgets.QHBoxLayout()
        save_file_layout.addWidget(self.save_file_label)
        save_file_layout.addWidget(self.save_file_path)
        return save_file_layout

    @staticmethod
    def set_error_log():
        error_log = QtWidgets.QLabel("Allah casts it's blessings upon us!")
        error_log.setMinimumSize(400, 20)
        error_log.setMaximumSize(600, 20)
        return error_log

    def get_user_input(self):
        self.scraper_parameter = self.get_scraper_parameter()
        number_of_links = self.handle_number_of_links()
        save_directory_path = self.get_save_location_path(self.save_file_path.text())
        save_file_path = os.path.join(save_directory_path, self.create_file_name())
        return self.scraper_parameter, number_of_links, save_file_path

    def execute_scraping(self, *args, **kwargs):
        """Here we get and format all the user input"""
        self.button.setEnabled(False)
        self.error_log.setText("Allah casts it's blessings upon us!")
        self.scraper_parameter, number_of_links, save_file_path = self.get_user_input()
        if not self.scraper_parameter:
            self.error_log.setText("No query or links given")
            self.button.setEnabled(True)
            return
        self.setup_thread(self.scraper_parameter, number_of_links, save_file_path)
        self.thread.start()

    def setup_thread(self, scraper_parameter, number_of_links, save_file_path):
        self.thread = QThread()
        self.worker = ArticleWorker(scraper_parameter, number_of_links, save_file_path)
        self.progress_counter.current_index = 0
        self.progress_counter.number_of_links = number_of_links
        self.worker.moveToThread(self.thread)
        self.connect_scraper_signals()

    def connect_scraper_signals(self):
        self.thread.started.connect(self.worker.run_article_scraper)
        self.worker.progress_bar.connect(self.progress_counter.update_index)
        self.worker.no_internet.connect(lambda: self.error_log.setText("No Internet access!"))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.progress_counter.restart_progress_counter)
        self.worker.finished.connect(lambda: self.button.setEnabled(True))

    def get_scraper_parameter(self):
        query = self.query.text()
        dummy_query = self.query.text().replace(" ", '')
        links = self.links_text_box.toPlainText()
        if dummy_query != '':
            return query
        elif links != '':
            return self.return_links_as_list(links)
        else:
            return False

    @staticmethod
    def return_links_as_list(links):
        links_list = links.split(',')
        for idx in range(len(links_list)):
            links_list[idx] = links_list[idx].replace(" ", "")  # could have removed the newline here as well
        links_list = [x for x in links_list if x not in ['', ",", "\n", "\'", "\""]]
        return list(dict.fromkeys(links_list))

    def handle_number_of_links(self):
        if type(self.scraper_parameter) is list:
            return len(self.scraper_parameter)
        number_of_links = self.number_links.text()
        if number_of_links == '':
            return DEFAULT_NUMBER_OF_LINKS
        try:
            number_of_links = int(number_of_links)
            if 0 < number_of_links <= MAX_NUMBER_OF_LINKS:
                return number_of_links
            else:
                self.error_log.setText("Invalid number given! Scraping <b>{}</b> links".format(DEFAULT_NUMBER_OF_LINKS))
                return DEFAULT_NUMBER_OF_LINKS
        except ValueError:
            self.error_log.setText("Invalid number given! Scraping <b>{}</b> links".format(DEFAULT_NUMBER_OF_LINKS))
            return DEFAULT_NUMBER_OF_LINKS

    def get_save_location_path(self, path):
        """This was the only way to get user input of path so that os.path.exists works properly"""
        if path != '':
            directories = [path.split('\\')[idx] for idx in range(len(path.split('\\')))][1:]
            if not directories:
                self.error_log.setText(
                    "Such directory doesn't exist! File will be saved to the default directory!")
                return DEFAULT_ARTICLES_DIRECTORY
            path = r'C:\{}'.format(os.path.join(*directories))
            if not os.path.exists(path):
                self.error_log.setText(
                    "Such directory doesn't exist! File will be saved to the default directory!")
                return DEFAULT_ARTICLES_DIRECTORY
            return path
        return DEFAULT_ARTICLES_DIRECTORY

    def create_file_name(self):
        now = datetime.datetime.now()
        if type(self.scraper_parameter) is str:
            self.file_name = self.scraper_parameter
        else:
            self.file_name = 'links'
        return self.file_name + now.strftime("__%m_%d__%Hh_%Mm_%Ss") + DEFAULT_FILE_EXTENSION

    def set_memento(self):
        if os.path.isfile(MEMENTO_FILE_PATH):
            with open(MEMENTO_FILE_PATH, 'rb') as f:
                memento = pickle.load(f)
            self.number_links.setText(memento['number_of_links'])
            self.save_file_path.setText(memento['save_file_path'])

    def get_memento(self):
        memento = {'number_of_links': self.number_links.text(), 'save_file_path': self.save_file_path.text()}
        return memento

    def closeEvent(self, a0):
        super(CentralWidget, self).closeEvent(a0)
        if os.path.isfile(MEMENTO_FILE_PATH):
            with open(MEMENTO_FILE_PATH, 'r+') as f:
                f.truncate(0)
        memento = self.get_memento()
        with open(MEMENTO_FILE_PATH, 'wb') as file:
            pickle.dump(memento, file)
