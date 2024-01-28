from docx import Document
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
from articles_scraper import ArticlesScraper


class ArticleWorker(QObject):
    progress_bar = pyqtSignal()
    no_internet = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, scraper_parameter, number_of_links, save_file_path):
        super().__init__()
        self.scraper_parameter = scraper_parameter
        self.number_of_links = number_of_links
        self.save_file_path = save_file_path

    def run_article_scraper(self):
        self.progress_bar.emit()
        a = ArticlesScraper(self.scraper_parameter, self.number_of_links, self.progress_bar)
        if not a.result:
            self.no_internet.emit()
        else:
            a.result.save(self.save_file_path)
        self.finished.emit()


class ArticlesProgressCounter(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        self.current_index = 0
        self.number_of_links = 0
        self.setText('Progress Counter')
        self.setMinimumSize(300, 20)
        self.setMaximumSize(600, 20)

    def update_index(self):
        if self.current_index == 0:
            self.setText("Scraping started!")
        else:
            self.setText('<b>' + str(self.current_index) + "/" + str(self.number_of_links) + '</b>' + '  articles')
        self.current_index += 1

    def restart_progress_counter(self):
        self.current_index = 0
        self.setText("Scraping done!")
