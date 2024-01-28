import collections
import inspect

from filters.daily_filter import DailyFilter
from filters.filters_constants import MAX_TICKERS, METHOD_HIERARCHY
from filters.hourly_filter import HourlyFilter



params = [
    {'daily': True,
     'filter': 'TickerType',
     'params': {'ticker_type': 'CS'}},
    {'daily': True,
     'filter': 'ATR',
     "params": {'days_count': 5, 'percent': 2, 'compare_sign': '>', 'win_size': 10, 'ignore_today_data': False}},
    {'daily': True,
     'filter': 'PercentChange',
     'params': {'days_count': 7, 'percent': 1, 'field': 'close', 'compare_sign': '>', 'ignore_today_data': False}},
    {'daily': True,
     'filter': 'AverageChange',
     'params': {'days_count': 3, 'percent': 2, 'field': 'volume', 'compare_sign': '>',
                'abs_value': True, 'ignore_today_data': False}},
    {'daily': True,
     'filter': 'AbsValue',
     'params': {'value': 30000, 'field': 'volume', 'compare_sign': '>', 'ignore_today_data': True}},
    {'daily': True,
     'filter': 'AbsChange',
     'params': {'days_count': 4, 'value': 30000, 'field': 'volume', 'compare_sign': '>', 'ignore_today_data': True}},
    {'daily': False,
     'filter': 'PercentChange',
     'params': {'hour_count': 5, 'percent': -1.5, 'field': 'open', 'compare_sign': '<', 'pre_market': False,
                'abs_value': False}},
    {'daily': False,
     'filter': 'AverageChange',
     'params': {'hour_count': 3, 'percent': 3, 'field': 'open', 'compare_sign': '<',
                'pre_market': True, 'abs_value': False}},
    {'daily': False,
     'filter': 'AbsValue',
     'params': {'value': 20, 'field': 'volume', 'compare_sign': '>', 'pre_market': False}}
]


def get_methods_by_name(cls, starts_with='filter_by', exclude=[]):
    return {key.split('_')[-1]: inspect.getfullargspec(foo) for key, foo in
            inspect.getmembers(cls, predicate=inspect.isfunction)
            if (key.startswith(starts_with)
                and (all([excl not in key for excl in exclude]) if len(exclude) else True)
                )}


FILTERS = collections.OrderedDict({'Daily': get_methods_by_name(DailyFilter, exclude=['TickerType']),
                                   'Hourly': get_methods_by_name(HourlyFilter, )})


class FilterManager:
    def __init__(self, params, api_key):
        self.params = params
        self.tickers = []
        self.daily_filter_params, self.hourly_filter_params = self.handle_params(self.params)
        df = DailyFilter()
        self.tickers = self.apply_filters(df, self.daily_filter_params)
        hf = HourlyFilter(self.tickers)
        self.tickers = self.apply_filters(hf, self.hourly_filter_params)

        """DailyField class have and sort method by ticker field"""
        self.tickers = self.cut_tickers_if_too_many(df.sort_tickers_by_field)

    @staticmethod
    def handle_params(params):
        """Returns two lists with daily and hourly filters"""
        daily_filter_params = [param for param in params if param['daily']]
        hourly_filter_params = [param for param in params if not param['daily']]
        return daily_filter_params, hourly_filter_params

    def cut_tickers_if_too_many(self, sort_tickers_by_field, max_tickers=MAX_TICKERS, field='volume'):
        """
        Returns slice of the list_of tickers
        if their count is greater than max_tickers
        """
        if len(self.tickers) > max_tickers:
            self.tickers = sort_tickers_by_field(self.tickers, field=field)
            return self.tickers[:max_tickers]
        else:
            return self.tickers

    @staticmethod
    def filter_by_priority(lst):
        """Filter func that sort list by METHOD_HIERARCHY"""

        return METHOD_HIERARCHY[lst['filter']]

    def priority_checker(self, params):
        """Sort list of filter methods by priority"""
        params.sort(key=self.filter_by_priority)
        return params

    def apply_filters(self, filter_method, params):
        """
        Execute filter methods one by one with theirs relevant parameters
        The try except check if filter parameters are incorrect
        """
        sorted_params = self.priority_checker(params)
        for param in sorted_params:
            try:
                self.tickers = getattr(filter_method, "filter_by_" + param['filter'])(**param['params'])
            except (KeyError, TypeError):
                pass
        return self.tickers


if __name__ == "__main__":
    fm = FilterManager(params)
    print(fm.tickers)
