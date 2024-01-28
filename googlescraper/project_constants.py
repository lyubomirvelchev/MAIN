import os
import pathlib

DEFAULT_NUMBER_OF_LINKS = 8
MAX_NUMBER_OF_LINKS = 40

ROOT_DIR = pathlib.Path().resolve()
MEMENTO_FILE_PATH = os.path.join(ROOT_DIR, 'memento.pickle')
DEFAULT_ARTICLES_DIRECTORY = os.path.join(ROOT_DIR, 'docx_articles')
DEFAULT_FILE_EXTENSION = '.docx'
