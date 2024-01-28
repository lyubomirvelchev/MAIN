import collections
import datetime

import pandas as pd
import numpy as np

from monitoring.download_minute_data import DownloadMinuteData
from screen.enum_data.enum_obj import TimeFrames, DailyFields
from utils import func_exec_timer


class PreparePrevDataV2:
    def __init__(self, params, tickers, api_key):
        self.tickers = tickers
        self.params = params
        self.api_key = api_key

        minute_downloader = DownloadMinuteData(self.params, self.tickers, api_key)
        self.prev_min_data = minute_downloader.minute_data

        self.field_timeframe_dict = self.unpack_params()
        self.previous_data = self.prepare_previous_data()
        self.current_time = self.get_current_download_time(self.prev_min_data)

    @staticmethod
    def get_current_download_time(prev_min_data):
        field = list(prev_min_data.keys())[0]
        return prev_min_data[field].index[-1] + datetime.timedelta(minutes=1)

    @staticmethod
    def aggregate_data(df, field):
        aggr_data = {}

        def aggr_open(ticker_data):
            if ticker_data.first_valid_index() is not None:
                return ticker_data.loc[ticker_data.first_valid_index()]
            return np.NaN

        def aggr_high(ticker_data):
            return ticker_data.max()

        def aggr_low(ticker_data):
            return ticker_data.min()

        def aggr_close(ticker_data):
            if ticker_data.last_valid_index() is not None:
                return ticker_data.loc[ticker_data.last_valid_index()]
            return np.NaN

        def aggr_volume(ticker_data):
            result = ticker_data.sum()
            if result != np.NaN:
                return result
            return 0

        def aggr_vwap(ticker_data):
            # return close as close ???
            if ticker_data.last_valid_index() is not None:
                return ticker_data.loc[ticker_data.last_valid_index()]
            return np.NaN

        fields_funcs = {'o': aggr_open, 'h': aggr_high, 'l': aggr_low, 'c': aggr_close, 'v': aggr_volume,
                        'vw': aggr_vwap}
        for ticker in df.columns:
            aggr_data[ticker] = fields_funcs[DailyFields[field].value](df[ticker])
        return aggr_data

    def create_aggregated_timeframe(self, field, timeframe):
        aggregate_data = pd.DataFrame()
        data = self.prev_min_data[DailyFields[field].value]

        start_timestamp = data.index[0].replace(hour=8, minute=0, second=0)
        # TODO what if the first data is not from 8:00 ?
        index = 0
        while True:
            period_indices = [start_timestamp + datetime.timedelta(minutes=period) for period in range(TimeFrames[timeframe].value)]
            idx_filter = data.index.isin(period_indices)
            filtered_df = data.loc[idx_filter]
            if not filtered_df.empty:
                period_aggregate = self.aggregate_data(data.loc[idx_filter], field)
                aggregate_data = pd.concat([aggregate_data, pd.DataFrame(data=period_aggregate, index=[start_timestamp])])
            start_timestamp += datetime.timedelta(minutes=TimeFrames[timeframe].value)
            if start_timestamp > data.index[-1]:
                break
        # return aggregate_data.dropna(how='all')
            index += 1
        return aggregate_data

    def unpack_params(self):
        """
        Add field name as key and timeframe as value to
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
        return tuples

    @func_exec_timer
    def prepare_previous_data(self):
        # data = {field: self.prev_min_data[field] for field in self.prev_min_data}
        previous_data = {}
        for field, timeframes in self.field_timeframe_dict.items():
            previous_data[field] = {}
            for timeframe in timeframes:
                previous_data[field][timeframe] = self.create_aggregated_timeframe(field, timeframe)
        return previous_data

