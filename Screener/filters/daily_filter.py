import datetime
import pandas as pd

from os import path
from polygon import RESTClient

from filters.daily_downloader import DailyDownloader
from filters.filters_constants import LIMIT, LOCALE_TYPE, MARKET_TYPE, PICKLES_FILES_DIRECTORY, API_KEY
from screen.enum_data import ComparisonOperators, DailyFields


class DailyFilter:
    def __init__(self):
        DailyDownloader()
        self.available_tickers = self.init_tickers()
        self.tickers = self.available_tickers

    @staticmethod
    def get_open_market_data():
        """
        Download available data from today,
        if market is open
        """

        formatted_date = str(datetime.date.today())
        with RESTClient(API_KEY) as client:
            response = client.stocks_equities_grouped_daily(
                locale=LOCALE_TYPE, market=MARKET_TYPE, date=formatted_date)
            if response.queryCount == 0:
                return False

            return response.results

    def init_tickers(self):
        """
        Initialize list of available tickets
        in downloaded data, that DailyFilter
        will modify
        """
        return list(self.load_df_from_pickle('open').index)

    @staticmethod
    def load_df_from_pickle(field):
        """
        load pickle data by selecting field name
        returns pandas DataFrame
        """
        current_file_path = path.join(PICKLES_FILES_DIRECTORY, DailyFields[field].value)
        selected_df = pd.read_pickle(current_file_path)
        return selected_df

    def create_additional_field_series(self, market_data, field):
        """
        The method modify market data to DataFrame
        and make filtration by 'self.tickers' to avoid diff
        between df indices

        returns pd.Series with selected field
        """
        market_data = pd.DataFrame(market_data)
        market_data.set_index('T', inplace=True)
        filter_fn = market_data.index.isin(self.tickers)
        filtered_market_data = market_data[filter_fn]
        return filtered_market_data[DailyFields[field].value]

    def get_daily_period(self, field, days_count, ignore_today_data=False):
        """
        The method loads DataFrame from selected field
        and if there are market data(the market is open today)
        add new column with the data for today

        returns the selected day period data
        """

        df_data = self.load_df_from_pickle(field)
        selected_df = pd.DataFrame(index=self.tickers, data=df_data)
        market_data = self.get_open_market_data()
        if market_data and ignore_today_data is False:
            additional_market_data = self.create_additional_field_series(market_data, field)
            selected_df['today'] = additional_market_data
        selected_daily_period_data = selected_df[selected_df.columns[-days_count:]]
        return selected_daily_period_data

    @staticmethod
    def filter_df(df, column_name, operator, value):
        """Filter DataFrame by selected column name,
        compare operator and value to compare

        Returns filtered DataFrame
        """
        filter_data_func = df[column_name].apply(lambda x: operator.value(x, value))
        filtered_result_data = df[column_name].loc[filter_data_func]
        return filtered_result_data

    def filter_by_AbsValue(self, value, field, compare_sign, ignore_today_data=True):
        """
            Filter data for selected period by absolute value of the field.
            When ignore_today_data is True the filtration includes today's data,
            and when is False get previous date.

            returns and modifies 'self.tickers'
            """
        data = self.get_daily_period(field, 1, ignore_today_data=ignore_today_data)
        filtered_result_data = self.filter_df(
            data, data.columns[0], ComparisonOperators[compare_sign], value)
        self.tickers = list(filtered_result_data.index)
        return self.tickers

    def filter_by_AbsChange(
            self, days_count, value, field, compare_sign, ignore_today_data=False):
        """
        Filter data for selected period and add two additional fields
        to selected_daily_period_data. One for %_diff and one for abs diff.
        When abs_value is False the filtration is by absolute value change,
        and when is True the filtration is by percent_change

        returns and modifies 'self.tickers'
        """

        selected_daily_period_data = self.get_daily_period(field, days_count, ignore_today_data=ignore_today_data)
        from_data = selected_daily_period_data.iloc[:, -1]
        to_data = selected_daily_period_data.iloc[:, 0]

        abs_diff = from_data.subtract(to_data)
        selected_daily_period_data['abs_diff'] = abs_diff
        filtered_result_data = self.filter_df(
            selected_daily_period_data, 'abs_diff', ComparisonOperators[compare_sign], value)
        self.tickers = list(filtered_result_data.index)
        return self.tickers

    def filter_by_PercentChange(
            self, days_count, percent, field, compare_sign, ignore_today_data=False):
        """
        Filter data for selected period and add two additional fields
        to selected_daily_period_data. One for %_diff and one for abs diff.
        When abs_value is False the filtration is by absolute value change,
        and when is True the filtration is by percent_change

        returns and modifies 'self.tickers'
        """

        selected_daily_period_data = self.get_daily_period(field, days_count, ignore_today_data=ignore_today_data)
        from_data = selected_daily_period_data.iloc[:, -1]
        to_data = selected_daily_period_data.iloc[:, 0]

        abs_diff = from_data.subtract(to_data)

        percent_change = (abs_diff.divide(from_data)) * 100
        selected_daily_period_data['%_change'] = percent_change
        filtered_result_data = self.filter_df(
            selected_daily_period_data, '%_change', ComparisonOperators[compare_sign], percent)

        self.tickers = list(filtered_result_data.index)
        return self.tickers

    def filter_by_AverageChange(
            self, days_count, percent, field, compare_sign, abs_value=False, ignore_today_data=False):
        """
        Filter data for selected period and add two additional fields
        to selected_daily_period_data. One for %_diff and one for abs diff.
        When abs_value is False the filtration is by absolute value change,
        and when is True the filtration is by percent_change

        returns and modifies 'self.tickers'
        """

        selected_daily_period_data = self.get_daily_period(field, days_count, ignore_today_data=ignore_today_data)
        from_date = selected_daily_period_data.iloc[:, -1]
        avg_value = selected_daily_period_data.sum(axis=1) / days_count
        abs_diff = from_date - avg_value

        if abs_value:
            selected_daily_period_data['abs_diff'] = from_date - avg_value
            filtered_result_data = self.filter_df(
                selected_daily_period_data, 'abs_diff', ComparisonOperators[compare_sign], percent)
        else:
            selected_daily_period_data['%Ch'] = (abs_diff / avg_value) * 100
            filtered_result_data = self.filter_df(
                selected_daily_period_data, '%Ch', ComparisonOperators[compare_sign], percent)
        self.tickers = list(filtered_result_data.index)
        return self.tickers

    def filter_by_ATR(self, days_count, percent, compare_sign, win_size=10, ignore_today_data=False):

        def calculate(frame, window_size):
            return round(frame.ewm(alpha=1 / window_size, adjust=False).mean(), 2)

        filtered_tickers = []

        df_close = self.load_df_from_pickle('close').loc[self.tickers]
        df_high = self.load_df_from_pickle('high').loc[self.tickers]
        df_low = self.load_df_from_pickle('low').loc[self.tickers]

        if ignore_today_data is False:
            df_close['today'] = self.get_daily_period('close', 1, ignore_today_data=False)
            df_high['today'] = self.get_daily_period('high', 1, ignore_today_data=False)
            df_low['today'] = self.get_daily_period('low', 1, ignore_today_data=False)

        for ticker in self.tickers:
            close = df_close.loc[ticker]
            high = df_high.loc[ticker]
            low = df_low.loc[ticker]
            tr0 = abs(high - low)
            tr1 = abs(high - close.shift())
            tr2 = abs(low - close.shift())
            tr = pd.Series(index=tr0.index, data=[max(tr0[idx], tr1[idx], tr2[idx]) for idx in range(len(tr0))])
            atr_values = calculate(tr, win_size)
            first_value = atr_values[-days_count]
            last_value = atr_values[-1]
            abs_change = last_value - first_value
            percent_change = (abs_change / first_value) * 100
            if ComparisonOperators[compare_sign].value(percent_change, percent):
                filtered_tickers.append(ticker)

        self.tickers = filtered_tickers
        return self.tickers

    def filter_by_TickerType(self, ticker_type):
        """
        Filter ticker by selected ticker type :
            ['CS', 'ADRC', 'ADRP', 'ADRR', 'UNIT', 'RIGHT',
            'PFD', 'FUND', 'SP', 'WARRANT', 'INDEX', 'ETF', 'ETN'],
        by default selected market:'stocks'
        and ticker limit with default value of 1000
        (1000 is max value)

        returns modify 'self.tickers'
        with selected ticker_type
        """

        all_selected_tickers = []
        with RESTClient(API_KEY) as client:
            selected_stocks = client.reference_tickers_v3(limit=LIMIT, type=ticker_type, market=MARKET_TYPE)
            all_selected_tickers.extend(selected_stocks.results)
            while hasattr(selected_stocks, 'next_url'):
                selected_stocks = client.reference_tickers_v3(
                    limit=1000, type=ticker_type, market=MARKET_TYPE, next_url=selected_stocks.next_url)
                all_selected_tickers.extend(selected_stocks.results)
            self.tickers = [elem['ticker'] for elem in all_selected_tickers]

        self.tickers = [ticker for ticker in self.tickers if ticker in self.available_tickers]

        return self.tickers

    def sort_tickers_by_field(self, tickers, field='volume'):
        """
        Returns list of available tickets,
        by getting the index of pandas DataFrame
        sorted by volume descending, from downloaded
        data, that DailyFilter will modify
        """

        """get the last added column"""
        latest_data_col = self.load_df_from_pickle(field).iloc[:, -1:]

        """sort selected df column by field in descending order"""
        sorted_available_tickers = latest_data_col.sort_values(by=[latest_data_col.columns[0]], ascending=False)

        """apply ticker list to select only the indices in 'tickers' """
        filtered_idx = latest_data_col.sort_values(by=[latest_data_col.columns[0]], ascending=False).index.isin(tickers)

        return list(sorted_available_tickers.iloc[filtered_idx].index)


if __name__ == "__main__":
    d_filter = DailyFilter()

    b = d_filter.filter_by_absolute_change(5, 1000, 'close', '<=', ignore_today_data=True)

    print(d_filter.tickers)
    print(len(d_filter.tickers))
