import datetime
import pandas as pd
import pytz

from multiprocessing import Pool
from pandas.tseries.holiday import USFederalHolidayCalendar
from polygon import RESTClient

from screen.enum_data import DailyFields


class DownloadMinuteData:
    TIMESPAN = 'minute'
    MULTIPLAYER = 1
    DOWNLOAD_DAYS_NEEDED = 4

    def __init__(self, params, tickers, api_key):
        self.tickers = tickers
        self.params = params
        self.api_key = api_key
        self.today_dt = datetime.datetime.now(tz=pytz.utc)
        self.today_str = self.today_dt.strftime('%Y-%m-%d')
        self.holidays = USFederalHolidayCalendar().holidays(start='2020-01-01', end=self.today_str)
        self.minute_data = self.get_minute_data()

    def get_previous_business_day(self, number_of_previous_days_left, last_date):
        """Ugly as fuck! Recursive of course"""
        """
        Calculates previous day by get in mind that the last date 
        is weekend or holiday
        """
        if last_date.weekday() == 0:
            previous_day = last_date - datetime.timedelta(days=3)
        else:
            previous_day = last_date - datetime.timedelta(days=1)
        if previous_day.strftime('%Y-%m-%d') in self.holidays:
            return self.get_previous_business_day(number_of_previous_days_left, previous_day)
        elif number_of_previous_days_left != 1:
            return self.get_previous_business_day(number_of_previous_days_left - 1, previous_day)
        elif number_of_previous_days_left == 1:
            return previous_day

    @staticmethod
    def starmap_wrap(args):
        """Prepare args that are needed to multiprocess method map"""
        resp = args[0].stocks_equities_aggregates(*args[1:])
        ticker = args[1]
        return resp, ticker

    def get_ticker_data(self, multiplier, timespan, from_, to):
        """
        Download needed ticker data using multiprocess Pool
        in format ticker name: ticker data as dataframe
        (columns are o, h, l, v, vw; rows timestamps for current multiplier)

        """
        dictt = {}
        with RESTClient(self.api_key) as client:
            parallel_input_params = [(client, ticker, multiplier, timespan, from_, to) for ticker in self.tickers]
            # with Pool(10) as p:
            with Pool(2) as p:  # DEBUG
                response = p.map(self.starmap_wrap, parallel_input_params)
                for res in response:
                    if hasattr(res[0], 'results'):
                        ticker_df = pd.DataFrame(res[0].results)
                        ticker_df['t'] = pd.to_datetime(ticker_df['t'], unit='ms')
                        ticker_df.set_index('t', inplace=True)
                        dictt[res[1]] = ticker_df
        return dictt

    @staticmethod
    def prepare_field_dataframe(data, field):
        """
        Create pandas DataFrame with tickers data for the selected field.
        Columns are tickers data
        Rows are timestams
        """
        return pd.DataFrame(data={ticker: df[field] for ticker, df in data.items()})

    def get_minute_data(self):
        start_date = self.get_previous_business_day(self.DOWNLOAD_DAYS_NEEDED, self.today_dt)
        data = self.get_ticker_data(self.MULTIPLAYER, self.TIMESPAN, start_date.strftime('%Y-%m-%d'),
                                    self.today_str)

        dictt = {}
        for field in DailyFields:
            dictt[field.value] = self.prepare_field_dataframe(data, field.value)
        return dictt
