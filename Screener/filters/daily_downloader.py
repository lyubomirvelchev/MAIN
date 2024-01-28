import datetime
import numpy as np
import pandas as pd
import os
import shutil

from polygon import RESTClient

from filters.filters_constants import LOCALE_TYPE, MARKET_TYPE, FIRST_DATE, PICKLES_FILES_DIRECTORY, DAILY_DATA_PATH, \
    LAST_UPDATE_PATH, API_KEY
from screen.enum_data import DailyFields




def get_ticker_types():
    with RESTClient(API_KEY) as client:
        response = client.reference_ticker_types()

        return {value: key for key, value in response.results['types'].items()}


class DailyDownloader:

    def __init__(self, dates=None):
        if not self.all_necessary_directories_and_files_exist():
            self.generate_empty_necessary_directories_and_files()
        self.tickers = []
        self.tickers_info = {}
        self.last_saved_date_str = self.get_last_saved_date()
        self.first_date_str, self.second_date_str = self.get_dates(dates)
        self.dates = self.filter_dates()
        self.data = self.update_data()
        if self.data is not False:
            self.save_as_pickle()
            self.update_last_saved_date()

    @staticmethod
    def get_dates(dates):
        """
            Return the two dates as first and second if they are given, or return None for first date (it will later
            assigned as the last_saved_date) and the today date as str for the second date.
        """
        if dates is None:
            return None, str(datetime.date.today())
        else:
            return dates[0], dates[1]

    @staticmethod
    def get_last_saved_date():
        """Read the date of the most recent update and return it as string."""
        with open(LAST_UPDATE_PATH) as file:
            return file.read()

    @staticmethod
    def all_necessary_directories_and_files_exist():
        """Check if we have all needed directories and files to execute the update. If not: return False."""
        if os.path.exists(PICKLES_FILES_DIRECTORY) and os.path.exists(LAST_UPDATE_PATH):
            for field in DailyFields:
                if not os.path.exists(os.path.join(PICKLES_FILES_DIRECTORY, field.value)):
                    return False
            return True
        return False

    @staticmethod
    def generate_empty_necessary_directories_and_files():
        """
            If some required files or directories are missing, this method is called and it creates new empty files
            and directories.
        """
        if os.path.isdir(DAILY_DATA_PATH):
            shutil.rmtree(DAILY_DATA_PATH)
        os.makedirs(PICKLES_FILES_DIRECTORY)
        open(LAST_UPDATE_PATH, 'x')
        with open(LAST_UPDATE_PATH, 'w') as file:
            file.write(FIRST_DATE)

    @staticmethod
    def daily_request_client(date):
        """
            Get a request from polygon with daily info for all ticker in the market and return the response or False if
            the query is empty.
        """
        formatted_date = date.strftime('%Y-%m-%d')
        if formatted_date == str(datetime.date.today()):
            """Don't download data from today"""
            return False
        with RESTClient(API_KEY) as client:
            response = client.stocks_equities_grouped_daily(
                locale=LOCALE_TYPE, market=MARKET_TYPE, date=formatted_date)
            if response.queryCount == 0:
                return False

            return response.results

    def filter_dates(self):
        """
            Get all business days between the first and second date and remove all dates that are before the
            last_saved_date. Also remove the today's date if it is within range. Return the dates from the last update
            up to the previous business date.
        """
        if self.first_date_str is None:
            first_date = datetime.datetime(*[int(x) for x in self.last_saved_date_str.split("-")])
        else:
            first_date = datetime.datetime(*[int(x) for x in self.first_date_str.split("-")])
        second_date = datetime.datetime(*[int(x) for x in self.second_date_str.split("-")])
        dates = pd.date_range(start=first_date, end=second_date, freq='B').to_pydatetime()
        if self.second_date_str == str(datetime.date.today()):
            dates = np.delete(dates, -1)
            self.second_date_str = str(datetime.date.today() + datetime.timedelta(days=-1))
        if self.last_saved_date_str is not None:
            last_saved_date = datetime.datetime(*[int(x) for x in self.last_saved_date_str.split("-")])
            dates = [date for date in dates if date > last_saved_date]
        return dates

    def update_data(self):
        """
            This method reads the info from the polygon response for every single date and saves the data in a
            dataframe. Also append all tickers in a list.
        """
        for date in self.dates:
            # TODO: Investigate double download
            response = self.daily_request_client(date)
            if response:
                daily_df = pd.DataFrame(response)
                daily_df.drop(columns=['n'], inplace=True)
                daily_df.set_index('T', inplace=True)
                self.tickers_info[date] = daily_df
                self.tickers.extend(daily_df.index.array)

        return self.return_dictionary_with_dataframes()

    def return_dictionary_with_dataframes(self):
        """Remove all tickers that are duplicated. Order the dataframes in a dictionary and return that dictionary."""
        self.tickers = list(dict.fromkeys(self.tickers))

        df_mapper = {key.value: pd.DataFrame(index=self.tickers) for key in DailyFields}
        for day, daily_df in self.tickers_info.items():
            for info in daily_df.columns:
                if not info == 't':
                    df_mapper[info][day] = daily_df[info]

        return df_mapper

    def save_as_pickle(self):
        """
            Connect the saved dataframe with the newly generated dataframe and save the concatenated_dataframe as
            pickle. For every field in DailyFields, a specific dataframe is saved as pickle.
        """
        for field in DailyFields:
            current_file_path = os.path.join(PICKLES_FILES_DIRECTORY, field.value)
            try:
                loaded_file = pd.read_pickle(current_file_path)
                concatenated_dataframe = pd.concat([loaded_file, self.data[field.value]], axis=1)
            except FileNotFoundError:
                concatenated_dataframe = self.data[field.value]
            if field.value == 'v' or field.value == 'n':
                """transform volume dataframe with floats into dataframe with integers"""
                columns = concatenated_dataframe.columns
                concatenated_dataframe = concatenated_dataframe[columns].fillna(0.0).astype(int)
            pd.to_pickle(concatenated_dataframe, current_file_path)

    def update_last_saved_date(self):
        """If any changes are made to the pickle files, update the date of last modification in last_update.txt."""
        with open(LAST_UPDATE_PATH, 'r+') as file:
            file.truncate()
            file.write(self.second_date_str)


if __name__ == '__main__':
    download = DailyDownloader()
