import multiprocessing as mp
import datetime

import pandas as pd
import atexit
import time

from polygon import RESTClient

from filters.filters_constants import LIMIT, MARKET_TYPE, API_KEY
from indicators import indicators
from monitoring.alert_manager import AlertManager
from monitoring.prepare_previous_data_V2 import PreparePrevDataV2
from monitoring.process_manager import AggregateCalculator, SocketMonitor
from monitoring.update_minute_data_V2 import UpdateMinuteDataV2
from monitoring.utils import func_exec_timer

# TICKERS = ["AAPL", "TSLA", "AMD", "XLF", 'AMC', 'MSFT', 'AA', 'NVDA', 'PLTR', 'VALE',
#            'SPCE', 'ZNGA', 'AMZN', 'RBLX', 'SOFI', 'BAC', 'UBER', 'CTAS', 'ORLY', 'PAYX', 'CTSH', 'PDD', 'XLNX',
#            'XEL', ]
#            'MTCH', 'CPRT', 'OKTA', 'VRSK', 'ANSS', 'FAST', 'SWKS', 'NTES', 'SGEN', 'PCAR', 'CDW', 'PTON', 'SIRI',
#            'SPLK', 'VRSN', 'CERN', 'DLTR', 'INCY', 'CHKP', 'TCOM', 'FOXA', 'FOX', 'ALGN', 'CRWD', 'DXCM', 'EBAY',
#            'MNST', 'WDAY', 'KLAC', 'VRTX', 'BIIB', 'SNPS', 'KDP', 'TEAM', 'MRVL', 'LULU', 'EXC', 'CDNS', 'AEP', 'KHC',
#            'MAR', 'WBA', 'BIDU', 'MCHP']

TICKERS = ['IIM', 'MUA', 'GLQ', 'BOE', 'PFL', 'CCD', 'EOD', 'HIO', 'NS', 'PSB', 'RYAM']
# TICKERS = ['VALE', 'AMZN', 'MSFT', 'IIM', 'MUA', 'GLQ', 'BOE', 'NVDA']
# TICKERS = ['NVDA']

ALERT_CONDITIONS = {
    0: 'single',
    1: 'all',
    2: 'group'
}

PARAMS = {'indicator_params':
    {
        # 0: {"name": "StockPrice", "params": {"field": 'close', "time_frame": '1min'}, "alerts": {'<': 900000}},
        # 1: {"name": "MA", "params": {"win_size": 10, "field": 'close', "time_frame": '5min'}, 'alerts': {'<': 1000000}},
        # 2: {"name": "StockPrice", "params": {"field": 'close', "time_frame": '1min'}, 'alerts': {'<': 2000000}}},
        # 3: {"name": "EMA", "params": {"win_size": 7, "field": 'low', "time_frame": '1min'},
        #     'alerts': {'<': 3000000}},
        # 4: {"name": "EMA", "params": {"win_size": 12, "field": 'high', "time_frame": '1min'},
        #     'alerts': {'<': 3000000}},
        # 5: {"name": "EMA", "params": {"win_size": 40, "field": 'open', "time_frame": '1min'},
        #     'alerts': {'<': 3000000}},
        5: {"name": "RelativeVolume", "params": {"win_size": 4, "field": 'volume', "time_frame": '5min'},
            'alerts': {'<': 3000000}},
        6: {"name": "MA", "params": {"win_size": 14, "field": 'high', "time_frame": '3min'},
            'alerts': {'<': 3000000}},
        7: {"name": "EMA", "params": {"win_size": 9, "field": 'low', "time_frame": '3min'},
            'alerts': {'<': 3000000}},
        8: {"name": "RSI", "params": {"win_size": 4, "field": 'open', "time_frame": '3min'},
            'alerts': {'<': 3000000}},
        9: {"name": "RSI", "params": {"win_size": 4, "field": 'high', "time_frame": '3min'},
            'alerts': {'<': 3000000}},
        0: {"name": "RSI", "params": {"win_size": 4, "field": 'low', "time_frame": '3min'},
            'alerts': {'<': 3000000}},
        1: {"name": "RSI", "params": {"win_size": 4, "field": 'close', "time_frame": '3min'},
            'alerts': {'<': 3000000}}},
    # 9: {"name": "RSI", "params": {"win_size": 8, "field": 'high', "time_frame": '10min'},
    #     'alerts': {'<': 3000000}}},

    # 7: {"name": "MA_BETTER", "params": {"win_size": 4, "field": 'close', "time_frame": '2min'},
    #     'alerts': {'<': 3000000}},
    # 9: {"name": "EMA", "params": {"win_size": 20, "field": 'close', "time_frame": '1min'},
    #     'alerts': {'<': 3000000}}},
    # 4: {"name": "EMA", "params": {"win_size": 4, "field": 'close', "time_frame": '2min'},
    #     'alerts': {'<': 3000000}}},
    # 4: {"name": "VWAP", "params": {"field": 'vwap', "time_frame": '1min'}, 'alerts': {'<=': 40000}}},
    # 5: {"name": "STD", "params": {"name_1": {"name": "EMA", "params": {"win_size": 21, "field": 'close',
    #                                                                    "time_frame": '1min'}},
    #                               "name_2": {"name": "RSI", "params": {"win_size": 8, "field": 'close',
    #                                                                    "time_frame": '1min'}}},
    #     'alerts': {'<': 5000000}},
    # 6: {"name": "STD", "params": {"name_1": {"name": "EMA", "params": {"win_size": 21, "field": 'close',
    #                                                                    "time_frame": '2min'}},
    #                               "name_2": {"name": "EMA", "params": {"win_size": 8, "field": 'close',
    #                                                                    "time_frame": '2min'}}},
    #     'alerts': {'<': 6000000}},
    # 7: {"name": "STD", "params": {"name_1": {"name": "StockPrice",
    #                                          "params": {"field": 'close', "time_frame": '1min'}},
    #                               "name_2": {"name": "VWAP",
    #                                          "params": {"field": 'vwap', "time_frame": '1min'}}},
    #     'alerts': {'<': 700000}}},
    'alert_params': {'condition': ALERT_CONDITIONS[0]}
}

class MonitorManger:
    """
        This class initializes all required information, turns on the web socket and updates a table with indicator
        values for each ticker every second or every time a new aggregate is available.
    """

    def __init__(self, tickers, params, api_key=API_KEY):
        """
            Prepare and preload data for all tickers and all indicators in the params and run the monitoring process
        """
        self.tickers = tickers
        self.params = params['indicator_params']
        self.api_key = api_key
        self.time_frames_dict = self.get_time_frames_for_indicator(self.params)

        self.socket = SocketMonitor(self.tickers, api_key)
        self.socket.run_and_listen()

        agg_calc = AggregateCalculator(self.socket.raw_queue)
        self.minute_queue = agg_calc.minute_queue
        self.aggr_sec_queue = agg_calc.aggr_sec_queue

        # prep_vals = PreparePreviousData(self.params, self.tickers, api_key)

        previous_values = PreparePrevDataV2(self.params, self.tickers, api_key)
        self.previous_data_V2 = previous_values.previous_data
        # self.previous_data = prep_vals.previous_data
        self.current_minute = previous_values.current_time.minute
        self.indicators_dict = self.init_all_indicator(self.params)
        self.table = pd.DataFrame(data={k: val.indicator_values.iloc[-1] for k, val in self.indicators_dict.items()})
        self.min_up_V2 = UpdateMinuteDataV2()
        self.alerts_queue = mp.Queue()
        self.alert_manager = AlertManager(params['indicator_params'], params['alert_params'], self.alerts_queue)
        atexit.register(self.exit_now)

        while True:
            # self.monitoring_process()
            if self.aggr_sec_queue.qsize() != 0 or self.minute_queue.qsize() != 0:
                self.monitoring_process()
                return
            else:
                """HackerMan"""
                self.socket.message_queue.put('stop')
                self.socket.socket_monitor.terminate()
                agg_calc.aggregate_process.terminate()
                time.sleep(1)

                self.socket = SocketMonitor(self.tickers, self.api_key)
                self.socket.run_and_listen()
                agg_calc = AggregateCalculator(self.socket.raw_queue)
                self.minute_queue = agg_calc.minute_queue
                self.aggr_sec_queue = agg_calc.aggr_sec_queue
                time.sleep(5)

    @property
    def tickers(self):
        return self.__ticker

    @tickers.setter
    def tickers(self, value):
        tickers = self.check_tickers(value)
        if tickers:
            self.__ticker = value

    @staticmethod
    def check_tickers(tickers):
        def daily_request_client():
            all_selected_tickers = []
            with RESTClient(API_KEY) as client:
                selected_stocks = client.reference_tickers_v3(limit=LIMIT, market=MARKET_TYPE)
                all_selected_tickers.extend(selected_stocks.results)
                while hasattr(selected_stocks, 'next_url'):
                    selected_stocks = client.reference_tickers_v3(
                        limit=1000, market=MARKET_TYPE, next_url=selected_stocks.next_url)
                    all_selected_tickers.extend(selected_stocks.results)
                all_selected_tickers = [elem['ticker'] for elem in all_selected_tickers]

                return set(all_selected_tickers)

        available_tickers = daily_request_client()

        ticker_set = set()
        for ticker in tickers:
            ticker_set.add(ticker.strip())

        if available_tickers:
            result_set = ticker_set.intersection(available_tickers)
            # set_diff = list(set(tickers).difference(result_set))
            return list(result_set)

    @staticmethod
    def get_time_frames_for_indicator(params):
        """
            Return dictionary with all indicators' time frames as keys and list with indicator as values. This is
            needed for the minute update of the indicators.
        """
        dictt = {}
        tuples = []
        for key, indicator in params.items():
            if indicator['name'] != "STD":
                tuples.append((key, indicator['params']['time_frame']))
            else:
                tuples.append((key, indicator['params']['name_1']['params']['time_frame']))
        for item in tuples:
            if item[1] not in dictt.keys():
                dictt[item[1]] = [item[0]]
            else:
                dictt[item[1]].append(item[0])
        if '1min' not in dictt.keys():
            dictt['1min'] = []
        return dictt

    def init_all_indicator(self, params):
        """
            This method initializes all given indicators.
        """
        indicators = {}
        for key, value in params.items():
            kwargs = value['params']
            kwargs['current_minute'] = self.current_minute
            name = value['name']
            indicators[key] = self.init_single_indicator(name, self.previous_data_V2, kwargs)
        return indicators

    @staticmethod
    def init_single_indicator(name, previous_data, kwargs):
        """
            Given kwargs and name of the indicator, this method initializes that indicator with the those kwargs.
        """
        return getattr(indicators, name)(previous_data, **kwargs)

    # @func_exec_timer
    def second_updater(self, indicators_dict, alerts_queue, params, table, ticker_data, alert_updater, current_minute):
        # updating whole row at once
        current_ticker_data = {}
        ticker_name = list(ticker_data.keys())[0]
        current_ticker_data[ticker_name] = {}
        for key, indicator in indicators_dict.items():
            ticker_indicator_data = indicator.seconds_updater(ticker_data, self.previous_data_V2, ticker_name,
                                                              current_minute)
            current_ticker_data[ticker_name][key] = ticker_indicator_data
        print(current_ticker_data[ticker_name])
        table.loc[ticker_name] = pd.Series(current_ticker_data[ticker_name])
        current_ticker_data[ticker_name]['time'] = ticker_data[ticker_name]['s']

        # alert_updater(ticker_name, current_ticker_data)

    def monitoring_process(self):
        """
            This is the main loop of the monitoring part of the project. Here we get data and calculate indicator values
            from two queues; The first queue returns second aggregates every second for each ticker that has had a print
            and then we calculates all indicator values based on this information. Whenever we get a minute aggregate
            from the minute's queue, a process is triggered that updates indicators' dataframes, if the time frame
            aggregate is completed and calculates the new prevalues of those indicator. We do this only for indicators'
            that complete a full time frame (if we have an indicator with '5min' time frame we do this every fifth
            minute (:05, :10, :15 minutes and etc.)
             if we have a '1min' time frame we do this every minute)
        :return:
        """
        while True:
            # try:
            if not self.minute_queue.empty():
                """TODO: make better"""
                time.sleep(1)

                # updated_timeframes, self.current_minute = self.min_up.update_time_frames_data_new(self.previous_data,
                #                                                                                   self.minute_queue)
                updated_timeframes, self.current_minute = self.min_up_V2.update_time_frames_data_V2(
                    self.previous_data_V2, self.minute_queue)
                print("")
                print("------------------------------------------------------------------------------")
                print("")
                # print(updated_timeframes)
                print(self.current_minute)
                for time_frame in updated_timeframes:
                    for indicator in self.time_frames_dict[time_frame]:
                        self.indicators_dict[indicator].prevalues_formula(self.previous_data_V2)
            if not self.aggr_sec_queue.empty():
                ticker_data = self.aggr_sec_queue.get()
                print(ticker_data)
                if [*ticker_data.values()][0]['s'].minute >= self.current_minute:
                    """Only calculate data that is from current minute"""

                    self.second_updater(self.indicators_dict, self.alerts_queue, self.params, self.table,
                                        ticker_data,
                                        self.alert_manager.alert_updater, self.current_minute)
                # self.exit_now()

            # except Exception as e:
            #     print(e)
            #     self.socket.message_queue.put('stop')

    def exit_now(self):
        print("Exit!")
        self.socket.message_queue.put('stop')
        print("HUA")

        # if not self.alerts_queue.empty():
        #     while not self.alerts_queue.empty():
        #         print(self.alerts_queue.get())


if __name__ == '__main__':
    monitor = MonitorManger(TICKERS, PARAMS, API_KEY)
