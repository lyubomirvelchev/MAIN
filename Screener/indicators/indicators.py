import sys
import abc
from abc import ABC
import datetime
import copy

import pandas as pd
import numpy as np
from screen.enum_data.enum_obj import DailyFields, ComparisonOperators

TIME_FRAMES = {
    '1min': 1,
    '2min': 2,
    '3min': 3,
    '5min': 5,
    '6min': 6,
    '10min': 10,
    '15min': 15,
    '30min': 30,
    '60min': 60
}


class BaseIndicatorInterface(abc.ABC):
    """
        This class gives the structure that is required for every indicator. In order to minimize the time needed for
        the calculations, we split this process into four different methods. The fifth method is the same for each
        indicator and triggers an alert whenever a certain value (given by the user) is reached from the indicator.
    """

    @abc.abstractmethod
    def calculate_previous_values(self):
        """
            This formula should calculate the indicator values 2-4 days (based on time frame) before the current day.
        """
        ...

    @abc.abstractmethod
    def prevalues_formula(self, previous_data):
        """
            The whole idea of the prevalues is optimise the calculations that occur every second in the seconds_updater
            method. This method return a pd.Series with constants for each ticker that will be saved in self.prevalues.
            Example: MA_Indicator with win_size = 6. (The prevalues_formula sums the last 5 (win_size - 1) values and
            divides that sum with 6 (win_size) for each ticker. The result is treated as constant and later in the
            seconds_updater formula we just add the current_value divided by 6 (win_size) to this constant for each
            ticker.)
        """
        ...

    @abc.abstractmethod
    def seconds_updater(self, second_aggregate, previous_data, ticker, current_minute):
        """
            This is the formula that is called every second (or every time we have second aggregate) for each ticker
            and returns the current value of the indicator for each given ticker.
        """
        ...

    def aggregate_value(self, previous_data, second_aggr, field, time_frame, ticker):
        last_aggr_field = previous_data[field][time_frame][ticker].dropna().iloc[-1]
        second_aggr_field = second_aggr[ticker][DailyFields[field].value]
        if field == 'close' or field == 'vwap':
            return second_aggr_field
        elif field == 'high':
            if second_aggr_field > last_aggr_field:
                return second_aggr_field
            else:
                return last_aggr_field
        elif field == 'low':
            if second_aggr_field < last_aggr_field:
                return second_aggr_field
            else:
                return last_aggr_field
        elif field == 'open':
            return last_aggr_field
        elif field == 'volume':
            return last_aggr_field + second_aggr_field

    @staticmethod
    def alert_checker(alerts_queue, indicator_alerts, ticker_data_series, indicator):
        """
            This method compares the current value of the indicator with the given by the user threshold and in the
            event of crossover, an alert is added to the alerts_queue.
        """
        ticker_name = ticker_data_series.index[0]
        indicator_value = ticker_data_series[0]
        for compare_sign, val in indicator_alerts.items():
            if ComparisonOperators[compare_sign].value(indicator_value, val):
                message = f"{indicator} for {ticker_name}: {indicator_value} {compare_sign} {val}"
                alerts_queue.put(message)


class FieldValueIndicator(BaseIndicatorInterface, ABC):
    """
        This is the simplest indicator that gets the field value (open, close, volume) of the current second's
        aggregate and returns it.
    """

    def __init__(self, previous_data, field=None, time_frame=None, current_minute=None):
        self.previous_data = previous_data
        self.field = field
        self.time_frame = time_frame
        self.field_key = DailyFields[self.field].value
        self.indicator_values = self.calculate_previous_values()
        self.prevalues = self.prevalues_formula(self.previous_data)

    def calculate_previous_values(self):
        series = pd.DataFrame(self.previous_data[self.field][self.time_frame])
        return pd.DataFrame({ticker: series[ticker].dropna() for ticker in series.columns})

    def prevalues_formula(self, previous_data):
        return None

    def seconds_updater(self, second_aggregate, previous_data, ticker, current_minute):
        value = self.aggregate_value(previous_data, second_aggregate, self.field, self.time_frame, ticker)
        return round(value, 3)


class StockPrice(FieldValueIndicator, ABC):
    """
        Get the current price of the ticker.
    """

    def __init__(self, previous_data, field='close', time_frame='1min', current_minute=None):
        super().__init__(previous_data, field=field, time_frame=time_frame, current_minute=current_minute)


class VWAP(FieldValueIndicator, ABC):
    """
        Get the current Volume Weighted Average Price of the ticker.
    """

    def __init__(self, previous_data, field='vwap', time_frame='1min', current_minute=None):
        super().__init__(previous_data, field=field, time_frame=time_frame, current_minute=current_minute)


class MA(BaseIndicatorInterface, ABC):
    """
        Since both Moving Average and Exponential Moving Average (MA, EMA) have the same seconds and period_values
        updater, we have created a class that is inherited by both to remove redundant code and to follow the latest
        and most advanced OOP paradigms.
    """

    def __init__(self, previous_data, field=None, time_frame='1min', win_size=10, current_minute=None):
        self.previous_data = previous_data
        self.field = field
        self.time_frame = time_frame
        self.win_size = win_size
        self.field_key = DailyFields[self.field].value
        self.indicator_values = self.calculate_previous_values()
        self.prevalues = None
        self.prevalues_formula(self.previous_data)

    def calculate_previous_values(self):
        tickers = self.previous_data[self.field][self.time_frame].columns
        all_values = pd.DataFrame(
            {ticker: self.previous_data[self.field][self.time_frame][ticker] for ticker in tickers})
        ma_values = pd.DataFrame(
            {ticker: all_values[ticker].dropna().rolling(self.win_size, min_periods=1).mean() for ticker in tickers})
        return ma_values

    def prevalues_formula(self, previous_data):
        ...

    def seconds_updater(self, second_aggregate, previous_data, ticker, current_minute):
        if self.time_frame == '1min' or current_minute % TIME_FRAMES[self.time_frame] == 0:
            """No aggregation + sum last win_size-1 number of fields"""
            value = second_aggregate[ticker][self.field_key]
            value = value + sum(previous_data[self.field][self.time_frame][ticker].dropna()[-self.win_size + 1:])
        else:
            """Aggregation + sum last win_size number of fields without the last one (cuz it's incomplete aggregate)"""
            value = self.aggregate_value(previous_data, second_aggregate, self.field, self.time_frame, ticker)
            value = value + sum(previous_data[self.field][self.time_frame][ticker].dropna()[-self.win_size:-1])
        return round(value / self.win_size, 3)


class EMA(BaseIndicatorInterface, ABC):
    """
        Since both Moving Average and Exponential Moving Average (MA, EMA) have the same seconds and period_values
        updater, we have created a class that is inherited by both to remove redundant code and to follow the latest
        and most advanced OOP paradigms
    """

    def __init__(self, previous_data, field=None, time_frame='1min', win_size=10, current_minute=None):
        self.previous_data = previous_data
        self.field = field
        self.time_frame = time_frame
        self.win_size = win_size

        self.alpha = 2 / (self.win_size + 1)
        self.field_key = DailyFields[self.field].value
        self.indicator_values = self.calculate_previous_values()
        if not self.time_frame == '1min' and not current_minute % TIME_FRAMES[self.time_frame] == 0:
            self.indicator_values = self.indicator_values[:-1]  # drop last row cuz its incomplete data
        self.prevalues = pd.Series({ticker: self.indicator_values[ticker].dropna().iloc[-1] for ticker in
                                    self.indicator_values.columns}).apply(lambda x: x * (1 - self.alpha))

    def calculate_previous_values(self):
        values = self.previous_data[self.field][self.time_frame]
        indicator_values = {ticker: (values[ticker].dropna().ewm(alpha=2 / (self.win_size + 1), adjust=False)).mean()
                            for ticker in values.columns}
        return pd.DataFrame(indicator_values)

    def prevalues_formula(self, previous_data):
        current_aggr = previous_data[self.field][self.time_frame].iloc[-1]
        last_index = self.indicator_values.index[-1]
        tickers = [ticker for ticker in current_aggr.index if not np.isnan(current_aggr[ticker])]
        new_data = pd.Series(
            {ticker: self.prevalues[ticker] + (current_aggr[ticker] * self.alpha) for ticker in tickers})
        self.indicator_values = pd.concat([self.indicator_values, pd.DataFrame(data=new_data).T])
        self.indicator_values.rename(index={0: last_index + datetime.timedelta(minutes=TIME_FRAMES[self.time_frame])},
                                     inplace=True)
        for ticker in tickers:
            self.prevalues[ticker] = new_data[ticker] * (1 - self.alpha)

    def seconds_updater(self, second_aggregate, previous_data, ticker, current_minute):
        if self.time_frame == '1min' or current_minute % TIME_FRAMES[self.time_frame] == 0:
            value = second_aggregate[ticker][self.field_key]
        else:
            value = self.aggregate_value(previous_data, second_aggregate, self.field, self.time_frame, ticker)
        return round(self.prevalues[ticker] + (value * self.alpha), 3)


class RSI(BaseIndicatorInterface, ABC):
    """
        Relative Strength Index that indicates if a stock is being overbought or oversold.
    """

    def __init__(self, previous_data, field=None, time_frame='1min', win_size=10, current_minute=None):
        self.previous_data = previous_data
        self.field = field
        self.time_frame = time_frame
        self.win_size = win_size
        self.current_minute = current_minute
        self.field_key = DailyFields[self.field].value
        self.all_values = self.calculate_previous_values()
        self.indicator_values = self.all_values[0]
        self.prevalues = self.all_values[1]

    def calculate_previous_values(self):
        df_with_values = pd.DataFrame(self.previous_data[self.field][self.time_frame])
        prevalues_rsi = {}

        def _relative_strength(frame):
            frame = frame.dropna()
            diff_frame_ups = pd.Series(frame).diff()
            diff_frame_downs = diff_frame_ups.copy()

            diff_frame_ups[diff_frame_ups < 0] = 0
            up = pd.Series.ewm(diff_frame_ups, alpha=1 / self.win_size, min_periods=self.win_size).mean()

            diff_frame_downs[diff_frame_downs > 0] = 0
            down = pd.Series.ewm(diff_frame_downs, alpha=1 / self.win_size, min_periods=self.win_size).mean()
            down *= -1

            rs = up.div(down)
            if self.current_minute % TIME_FRAMES[self.time_frame] == 0:
                return rs, up[-1], down[-1], frame[-1]
            else:
                return rs, up[-2], down[-2], frame[-2]

        for ticker in df_with_values.columns:
            rs, up, down, last_field_value = _relative_strength(df_with_values[ticker])
            rsi = rs.apply(lambda x: 100 - (100 / (1 + x)))
            prevalues_rsi[ticker] = {'rsi': rsi, "up": up, "down": down, "previous_value": last_field_value}

        rsi_df = pd.concat([prevalues_rsi[ticker]['rsi'] for ticker in df_with_values.columns], axis=1)
        prevalues_rsi = pd.DataFrame(prevalues_rsi).T[['up', 'down', 'previous_value']]
        return rsi_df, prevalues_rsi

    def seconds_updater(self, second_aggregate, previous_data, ticker, current_minute):
        if self.time_frame == '1min' or current_minute % TIME_FRAMES[self.time_frame] == 0:
            value = second_aggregate[ticker][self.field_key]
        else:
            value = self.aggregate_value(previous_data, second_aggregate, self.field, self.time_frame, ticker)
        row = self.prevalues.loc[ticker]
        up = row['up']
        down = row['down']
        previous_value = row['previous_value']

        diff_up = value - previous_value if value - previous_value >= 0 else 0
        diff_down = value - previous_value if value - previous_value <= 0 else 0
        avg_up = up * (self.win_size - 1) / self.win_size + diff_up / self.win_size
        avg_down = (down * (self.win_size - 1)) / self.win_size + -diff_down / self.win_size
        rs = avg_up / avg_down
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 3)

    def prevalues_formula(self, previous_data):
        rsi = {}
        current_aggr = previous_data[self.field][self.time_frame].iloc[-1]
        tickers = [ticker for ticker in current_aggr.index if not np.isnan(current_aggr[ticker])]
        for ticker in tickers:
            current_value = current_aggr[ticker]
            row = self.prevalues.loc[ticker]
            up = row['up']
            down = row['down']
            previous_value = row['previous_value']

            """TODO: Check; Nan removed"""
            diff_up = current_value - previous_value if current_value - previous_value >= 0 else 0
            diff_down = current_value - previous_value if current_value - previous_value <= 0 else 0
            avg_up = up * (self.win_size - 1) / self.win_size + diff_up / self.win_size
            avg_down = (down * (self.win_size - 1)) / self.win_size + -diff_down / self.win_size
            rs = avg_up / avg_down
            rsi[ticker] = 100 - (100 / (1 + rs))
            self.prevalues.at[ticker, 'up'] = avg_up
            self.prevalues.at[ticker, 'down'] = avg_down
            self.prevalues.at[ticker, 'previous_value'] = current_value
        self.indicator_values = self.indicator_values.append(
            pd.Series(rsi, name=self.previous_data[self.field][self.time_frame].index[-1]))
        a = 8


class STD(BaseIndicatorInterface, ABC):
    """
        Standard deviation indicator that indicates the relative distance between two simple indicators compared to
        their usual (standard) distance.
    """

    def __init__(self, previous_data, name_1, name_2):
        self.previous_data = previous_data
        ind_1_params = name_1
        ind_2_params = name_2
        self.ind_1 = getattr(sys.modules[__name__], ind_1_params['name'])(self.previous_data,
                                                                          **ind_1_params['params'])
        self.ind_2 = getattr(sys.modules[__name__], ind_2_params['name'])(self.previous_data,
                                                                          **ind_2_params['params'])
        self.all_values = self.calculate_previous_values()
        self.indicator_values = self.all_values[0]
        self.prevalues = self.all_values[1]

    def calculate_previous_values(self):
        ind_1_values = pd.DataFrame(self.ind_1.indicator_values)
        ind_2_values = pd.DataFrame(self.ind_2.indicator_values)

        def window_foo(frame):
            return frame.expanding(2)

        def calculate(abs_diff, frame):
            return abs_diff.div(frame.std())

        std = pd.DataFrame()
        abs_diff = pd.DataFrame()
        for ticker in ind_2_values.columns:
            absolute_diff = ind_1_values[ticker] - ind_2_values[ticker]

            std[ticker] = round(calculate(absolute_diff, window_foo(absolute_diff)), 3)
            abs_diff[ticker] = absolute_diff

        return std, abs_diff

    def seconds_updater(self, second_aggregate, previous_data, ticker, current_minute):
        ind_1_current_value = self.ind_1.seconds_updater(second_aggregate)
        ind_2_current_value = self.ind_2.seconds_updater(second_aggregate)
        current_abs_diff = ind_1_current_value - ind_2_current_value
        abs_diff = self.prevalues
        df = abs_diff.append(current_abs_diff, ignore_index=True)
        return pd.Series(
            {ticker: df[ticker].iloc[-1] / df[ticker].std() for ticker in second_aggregate.keys()}).round(
            decimals=3)

    def prevalues_formula(self, previous_data):
        self.ind_1.prevalues_formula(previous_data)
        self.ind_2.prevalues_formula(previous_data)
        for timestamp, ticker_data in minute_aggregate.items():
            abs_diff = self.ind_1.indicator_values.iloc[-1] - self.ind_2.indicator_values.iloc[-1]
            self.prevalues = self.prevalues.append(pd.Series(abs_diff, name=timestamp))
            self.indicator_values = self.indicator_values.append(
                pd.Series({ticker: self.prevalues[ticker].iloc[-1] / self.prevalues[ticker].std() for ticker in
                           abs_diff.index}, name=timestamp))


class RelativeVolume(BaseIndicatorInterface, ABC):
    def __init__(self, previous_data, win_size=10, field=None, time_frame='1min', current_minute=None):
        self.win_size = win_size
        self.field = 'volume'
        self.field_key = DailyFields[self.field].value
        self.time_frame = time_frame
        self.current_minute = current_minute
        self.previous_data = previous_data
        self.indicator_values = self.calculate_previous_values()
        if self.time_frame == '1min' or current_minute % TIME_FRAMES[self.time_frame] == 0:
            previous_volumes = self.previous_data[self.field][self.time_frame].iloc[-self.win_size:]
        else:
            previous_volumes = self.previous_data[self.field][self.time_frame].iloc[-self.win_size - 1:-1]
        self.prevalues = previous_volumes.mean()
        print(self.prevalues)

    def calculate_previous_values(self):
        previous_volumes = self.previous_data[self.field][self.time_frame].iloc[-self.win_size - 1:-1]
        mean = previous_volumes.mean()
        current_aggr = self.previous_data[self.field][self.time_frame].iloc[-1]
        return pd.DataFrame((current_aggr.div(mean)) * 100)

    def prevalues_formula(self, previous_data):
        previous_volumes = self.previous_data[self.field][self.time_frame].iloc[-self.win_size:]
        self.prevalues = previous_volumes.mean()
        print(self.prevalues)

    def seconds_updater(self, second_aggregate, previous_data, ticker, current_minute):
        if self.time_frame == '1min' or current_minute % TIME_FRAMES[self.time_frame] == 0:
            value = second_aggregate[ticker][self.field_key]
        else:
            value = self.aggregate_value(previous_data, second_aggregate, self.field, self.time_frame, ticker)
        return round((value / self.prevalues[ticker]) * 100, 6)
