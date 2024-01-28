import pandas as pd
import os
import pathlib
import tqdm
from polygon import RESTClient
import datetime


DAILY_FIELDS = {'open': "o",
                'high': 'h',
                'low': 'l',
                'close': "c",
                'volume': "v",
                'vwap': "vw",
                "number": "n"}

ROOT_DIR = pathlib.Path().resolve()
DAILY_DATA_PATH = os.path.join(ROOT_DIR, "daily_data")
PICKLES_FILES_DIRECTORY = os.path.join(ROOT_DIR, "daily_data", "pickle_files")
TICKERS = ["AAPL", "TSLA", "AMD", "XLF", 'AMC', 'MSFT', 'AA', 'NVDA']

PARAMS = [{"ind": "StockPrice", "params": {}},
          {"ind": "EMA", "params": {"win_size": 8, "field": 'close', "time_frame": '1min'}},
          {"ind": "MA", "params": {"win_size": 8, "field": 'high', "time_frame": '13min'}},
          {"ind": "STD", "params": {"win_size": 21,
                                    "ind_1": {"ind": "StockPrice", "params": {}},
                                    "ind_2": {"ind": "EMA", "params": {"win_size": 8, "field": 'open',
                                                                       "time_frame": '1min'}}}},
          {"ind": "STD", "params": {"win_size": 21,
                                    "ind_1": {"ind": "EMA", "params": {"win_size": 21, "field": 'close',
                                                                       "time_frame": '15min'}},
                                    "ind_2": {"ind": "EMA", "params": {"win_size": 8, "field": 'close',
                                                                       "time_frame": '15min'}}}},
          {"ind": "STD", "params": {"win_size": 21,
                                    "ind_1": {"ind": "StockPrice", "params": {}},
                                    "ind_2": {"ind": "VWAP", "params": {}}}}]


class PreparePreviousData:
    def __init__(self, params):
        self.params = params
        self.field_timeframe_dict = self.unpack_params()

    @staticmethod
    def return_field_timeframe_tuples(params):
        tuples = []
        for indicator in params:
            if indicator['ind'] != "STD":
                field = indicator['params'].get('field', None)
                time_frame = indicator['params'].get('time_frame', None)
                tuples.append((field, time_frame))
            else:
                field1 = indicator['params']['ind_1']['params'].get('field', None)
                timeframe1 = indicator['params']['ind_1']['params'].get('time_frame', None)
                field2 = indicator['params']['ind_2']['params'].get('field', None)
                timeframe2 = indicator['params']['ind_2']['params'].get('time_frame', None)
                tuples.extend([(field1, timeframe1), (field2, timeframe2)])
        tuples = [tpl for tpl in tuples if None not in tpl]
        return tuples

    def unpack_params(self):
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


def convert_unix_timestamp(unix_timestamp):
    """
        Converts unix timestamp L{int} to L{datetime.datetime}.

        @param unix_timestamp: timestamp
        @type unix_timestamp: L{int}

        @rtype: L{datetime.datetime}
        @return: The L{datetime.datetime} that was converted from a timestamp
    """
    return datetime.datetime.fromtimestamp(unix_timestamp / 1000.0, tz=datetime.timezone.utc)


def getter(tickers, timespan, multiplier, from_, to):
    dataframes = {}
    for ticker in tickers:
        with RESTClient(API_KEY) as client:
            response = client.stocks_equities_aggregates(
                ticker=ticker, multiplier=multiplier, timespan=timespan, from_=from_, to=to,
                limit=50000)
            if response.queryCount != 0:
                df = pd.DataFrame(response.results)
                df["t"] = df["t"].apply(convert_unix_timestamp)
                df.set_index('t', inplace=True)
                dataframes[ticker] = df

    return dataframes


def load_df_from_pickle(field):
    """
    load pickle data by selecting field name
    returns pandas DataFrame
    """
    current_file_path = os.path.join(PICKLES_FILES_DIRECTORY, DAILY_FIELDS[field])
    selected_df = pd.read_pickle(current_file_path)
    return selected_df


def moving_average(win_size=8, time_frame='1D', field='open'):
    if time_frame == "1D":
        series = pd.read_pickle(os.path.join(PICKLES_FILES_DIRECTORY, DAILY_FIELDS[field]))
    return round((series.rolling(win_size, min_periods=1)).mean(), 3)


def exp_moving_average(tickers, win_size=8, time_frame='1D', field='high'):
    if time_frame == "1D":
        series = pd.read_pickle(os.path.join(PICKLES_FILES_DIRECTORY, DAILY_FIELDS[field]))
    return round((series.ewm(span=win_size, adjust=False)).mean(), 3)


def rsi(tickers, win_size=8, time_frame='1D', field='close'):
    series = pd.read_pickle(os.path.join(PICKLES_FILES_DIRECTORY, DAILY_FIELDS[field]))
    df = pd.DataFrame(index=series.columns)

    def _relative_strength(frame):
        diff_frame_ups = pd.Series(frame).diff()
        diff_frame_downs = diff_frame_ups.copy()

        diff_frame_ups[diff_frame_ups < 0] = 0
        up = pd.Series.ewm(diff_frame_ups, alpha=1 / win_size, ignore_na=True).mean()

        diff_frame_downs[diff_frame_downs > 0] = 0
        down = pd.Series.ewm(diff_frame_downs, alpha=1 / win_size, ignore_na=True).mean()
        down *= -1

        rs = up.div(down)
        return rs

    for ticker in tickers:
        hui = round(_relative_strength(series.loc[ticker]).apply(lambda x: 100 - (100 / (1 + x))), 2)
        df[ticker] = hui

    return df.T


def atr(tickers, win_size=8, time_frame='1D'):
    df_close = load_df_from_pickle('close')
    df_high = load_df_from_pickle('high')
    df_low = load_df_from_pickle('low')
    df = pd.DataFrame(index=df_close.columns)

    def calculate(frame, window_size):
        return round(frame.ewm(alpha=1 / window_size, adjust=False).mean(), 3)

    for ticker in tickers:
        close = df_close.loc[ticker]
        high = df_high.loc[ticker]
        low = df_low.loc[ticker]
        tr0 = abs(high - low)
        tr1 = abs(high - close.shift())
        tr2 = abs(low - close.shift())
        tr = pd.Series(index=tr0.index, data=[max(tr0[idx], tr1[idx], tr2[idx]) for idx in range(len(tr0))])
        atr_values = calculate(tr, win_size)
        df[ticker] = atr_values

    return df


def std(tickers, win_size=8, time_frame='1D', field='high'):
    ...


if __name__ == "__main__":
    b = PreparePreviousData(PARAMS)
    hui = getter(TICKERS, 'minute', 1, '2022-01-28', '2022-01-31')
    husgrfdhfi = getter(TICKERS, 'minute', 15, '2022-01-28', '2022-01-31')
    rsi = rsi(TICKERS)
    atr = atr(TICKERS)
    a = 7
