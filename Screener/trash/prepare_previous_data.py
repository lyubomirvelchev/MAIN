import datetime
import pandas as pd
import pytz

from multiprocessing import Pool
from pandas.tseries.holiday import USFederalHolidayCalendar
from polygon import RESTClient

from screen.enum_data import DailyFields
from monitoring.utils import func_exec_timer


class PreparePreviousData:
    """
    Class download needed ticker data, and creates structure
    with fields (open , close , low , etc ...) as keys and
    time frames (1min, 2min, 3min, etc ...) with dataframes with
    ticker[field] data
    """

    def __init__(self, params, tickers, api_key):
        self.tickers = tickers
        self.params = params
        self.api_key = api_key
        self.field_timeframe_dict = self.unpack_params()
        self.today_dt = datetime.datetime.now(tz=pytz.utc)
        self.today_str = self.today_dt.strftime('%Y-%m-%d')
        self.holidays = USFederalHolidayCalendar().holidays(start='2020-01-01', end=self.today_str)
        self.previous_data = self.get_indicators_specific_data()
        self.current_time = self.previous_data['close']['1min'].index[-1] + datetime.timedelta(minutes=1)

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
    def split_string_intervals(interval):
        """Get the int(time interval) and time interval"""
        if interval.find("min") == -1:
            return int(interval.split('hour')[0]), 'hour'
        else:
            return int(interval.split('min')[0]), 'minute'

    @staticmethod
    def get_the_number_of_additional_business_days_needed(multiplier, timespan):
        """
        Returns the required count of days to be downloaded
        depend on the timespan
        """
        if timespan == 'hour':
            number_of_previous_days_needed = 4
        else:
            if multiplier < 15:
                number_of_previous_days_needed = 2
            else:
                number_of_previous_days_needed = 3

        return number_of_previous_days_needed

    @staticmethod
    def prepare_nice_df(data, field):
        """
        Create pandas DataFrame with tickers data for the selected field.
        Columns are tickers data
        Rows are timestams for the current period
        """
        return pd.DataFrame(data={ticker: df[field] for ticker, df in data.items()})

    @staticmethod
    def return_field_timeframe_tuples(params):
        """Fill the tuple list with all tuples of (field and timeframe)"""
        tuples = []
        for indicator in params.values():
            if indicator['name'] != "STD":
                field = indicator['params'].get('field', None)
                time_frame = indicator['params'].get('time_frame', None)
                tuples.append((field, time_frame))
            else:
                field1 = indicator['params']['name_1']['params'].get('field', None)
                timeframe1 = indicator['params']['name_1']['params'].get('time_frame', None)
                field2 = indicator['params']['name_2']['params'].get('field', None)
                timeframe2 = indicator['params']['name_2']['params'].get('time_frame', None)
                tuples.extend([(field1, timeframe1), (field2, timeframe2)])
        tuples = [tpl for tpl in tuples if None not in tpl]
        if ('close', '1min') not in tuples:
            tuples.append(('close', '1min'))
        return tuples

    def unpack_params(self):
        """
        Add field name as key and timeftame as value to
        field_timeframe_dict = {field: timeframe}
        """
        tuples = self.return_field_timeframe_tuples(self.params)
        field_timeframe_dict = {}
        for tpl in tuples:
            if tpl[0] not in field_timeframe_dict:
                field_timeframe_dict[tpl[0]] = [tpl[1]]
            else:
                field_timeframe_dict[tpl[0]].append(tpl[1])
        for key in field_timeframe_dict.keys():
            non_duplicate_timeframes = list(dict.fromkeys(field_timeframe_dict[key]))
            field_timeframe_dict[key] = non_duplicate_timeframes
        return field_timeframe_dict

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
            with Pool(2) as p:
            # with Pool(2) as p:  # DEBUG
                response = p.map(self.starmap_wrap, parallel_input_params)
                for res in response:
                    if hasattr(res[0], 'results'):
                        ticker_df = pd.DataFrame(res[0].results)
                        ticker_df['t'] = pd.to_datetime(ticker_df['t'], unit='ms')
                        ticker_df.set_index('t', inplace=True)
                        dictt[res[1]] = ticker_df
        return dictt

    @func_exec_timer
    def get_indicators_specific_data(self):
        """
        Main method in this class:
        Iterate to all time intervals and get all needed info to
        collect ticker data and returns dicctt
        with {field(open, close, low, ets..): timeframe(1min, 2min, 3min, etc...), etc ...}
        """
        dictt = {}
        for field in self.field_timeframe_dict.keys():
            dictt[field] = {}
            for interval in self.field_timeframe_dict[field]:
                multiplier, timespan = self.split_string_intervals(interval)
                previous_days_needed = self.get_the_number_of_additional_business_days_needed(multiplier, timespan)
                start_date = self.get_previous_business_day(previous_days_needed, self.today_dt)
                data = self.get_ticker_data(multiplier, timespan, start_date.strftime('%Y-%m-%d'), self.today_str)
                nice_df = self.prepare_nice_df(data, DailyFields[field].value)
                dictt[field][interval] = nice_df
        return dictt
