import os
import pathlib
from os import path

# hourly_filter constants
MULTIPLIER = 1
DAY_HOURS = 24
TIME_INTERVAL = 'hour'

# filter_manager constants
METHOD_HIERARCHY = {
    "TickerType": 1,
    "AbsValue": 2,
    "PercentChange": 3,
    "AbsChange": 4,
    "AverageChange": 5,
    "ATR": 6
}
# max ticker count if daily filter returns too many tickers
MAX_TICKERS = 20

# polygon client named arguments
LIMIT = 1000
LOCALE_TYPE = 'us'
MARKET_TYPE = 'stocks'
FIRST_DATE = "2022-01-01"

# filters file path
ROOT_DIR = pathlib.Path().resolve()
PICKLES_FILES_DIRECTORY = path.join(ROOT_DIR, "daily_data", "pickle_files")

# daily data path
DAILY_DATA_PATH = os.path.join(ROOT_DIR, "daily_data")
LAST_UPDATE_PATH = os.path.join(DAILY_DATA_PATH, 'last_update.txt')

# market working hours
SUMMER_TIME_PRE_MARKET_HOURS_RANGE = [n for n in range(8, 23 + 1)]
SUMMER_TIME_MARKET_HOURS_RANGE = [n for n in range(14, 20 + 1)]
WINTER_TIME_PRE_MARKET_HOURS_RANGE = [n for n in range(9, 24 + 1)]
WINTER_TIME_MARKET_HOURS_RANGE = [n for n in range(15, 21 + 1)]

API_KEY = 'f7VRP_aWw41goYNDJwu_yJ4EFK4NL6K7'


