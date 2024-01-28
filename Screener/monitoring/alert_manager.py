import csv
import datetime
import os
import pandas as pd

from monitoring.monitoring_constants import ALERTS_FILE_PATH
from screen.enum_data import ComparisonOperators

ALERT_CONDITIONS = {
    0: 'single',
    1: 'all',
    2: 'group'
}

PARAMS = {'indicator_params':
    {
        0: {"name": "StockPrice", "params": {"field": 'close', "time_frame": '1min'}, "alerts": {'<': 5000}},
        1: {"name": "EMA", "params": {"win_size": 8, "field": 'close', "time_frame": '10min'}, 'alerts': {}},
        2: {"name": "RSI", "params": {"win_size": 6, "field": 'close', "time_frame": '15min'}, 'alerts': {}},
        3: {"name": "MA", "params": {"win_size": 6, "field": 'close', "time_frame": '1min'}, 'alerts': {}},
        4: {"name": "VWAP", "params": {"field": 'vwap', "time_frame": '1min'}, 'alerts': {'<=': 5000}},
        5: {"name": "STD", "params": {"name_1": {"name": "EMA", "params": {"win_size": 21, "field": 'close',
                                                                           "time_frame": '1min'}},
                                      "name_2": {"name": "RSI", "params": {"win_size": 8, "field": 'close',
                                                                           "time_frame": '1min'}}},
            'alerts': {'<': 1000}},
        6: {"name": "STD", "params": {"name_1": {"name": "EMA", "params": {"win_size": 21, "field": 'close',
                                                                           "time_frame": '2min'}},
                                      "name_2": {"name": "EMA", "params": {"win_size": 8, "field": 'close',
                                                                           "time_frame": '2min'}}},
            'alerts': {'<': 1000}},
        7: {"name": "STD", "params": {"name_1": {"name": "StockPrice",
                                                 "params": {"field": 'close', "time_frame": '1min'}},
                                      "name_2": {"name": "VWAP",
                                                 "params": {"field": 'vwap', "time_frame": '1min'}}},
            'alerts': {'<': 1000}}},
    'alert_params': {'condition': ALERT_CONDITIONS[1]}
}



TICKER_DATA = pd.Series(
    {'AAPL': {0: 14.75, 1: 50, 2: 150, 4: 6000}}
)


class AlertManager:
    """
    This class handles all alerts that are attached for every indicator.
    It's function is to fill the alert table and add alerts to alert message queue.
    """

    def __init__(self, indicator_params, alert_params, alerts_queue):
        self.indicator_alerts = self.get_indicators_alerts(indicator_params)
        self.alert_params = alert_params
        self.alerts_queue = alerts_queue
        self.alert_file = self.init_alerts_file_path()
        self.indicator_info = self.init_indicator_names_alerts_included(indicator_params)
        self.create_csv_info_data(self.alert_file, self.indicator_info, self.alert_params['condition'],
                                  self.indicator_alerts)
        self.alert_table = pd.DataFrame()

    def __del__(self):
        """
        when the method is called write all collected alert data to csv file
        """
        self.write_alert_data_to_csv(self.alert_file, self.alert_table)

    @staticmethod
    def get_indicators_alerts(indicator_params):
        """
        get all indicators that have alerts
        """
        return {indicator: values.get('alerts') for indicator, values in indicator_params.items() if
                values.get('alerts')}

    @staticmethod
    def alert_checker(indicator_alerts, indicator_value):
        """
        compare indicator value and the alert value and if condition
        returns alert message
        """
        for compare_sign, val in indicator_alerts.items():
            if ComparisonOperators[compare_sign].value(indicator_value, val):
                # message = f"{indicator} for {ticker_name}: {indicator_value} {compare_sign} {val}"
                message = f"'{indicator_value} {compare_sign} {val}'"
                return message
        return None

    def init_alert_list(self, indicator_value):
        """
        iterate to all indicators and its alerts and check's
        if any alerts - is_alerts and if any alerts fill the two
        dicts
        """
        # this dict is fill with all alerts include passes
        full_alert_data = {}
        # this dict is fill with all alerts exclude passes
        no_pass_alert_data = {}
        is_alerts = False
        for indicator in self.indicator_alerts:
            alert = self.alert_checker(self.indicator_alerts[indicator], indicator_value[indicator])
            if alert:
                is_alerts = True
                full_alert_data[indicator] = alert
                no_pass_alert_data[indicator] = alert
            else:
                full_alert_data[indicator] = "pass"
        return no_pass_alert_data, is_alerts, full_alert_data

    def alert_updater(self, ticker_name, ticker_data):
        """
        If is_alerts is False that means there is no alerts for all indicators
        and the func returns.
        When condition is == to ALERT_CONDITIONS[0], check for every single
        alert and if condition add message.
        When condition is == to ALERT_CONDITIONS[1], check for all alerts
        as one condition and if all have True add message
        alert as single.
        """

        # all single alert work as condition
        indicators_values = ticker_data[ticker_name]
        alerts, is_alerts, full_alert_data = self.init_alert_list(indicators_values)
        if not is_alerts:
            return
        if self.alert_params['condition'] == ALERT_CONDITIONS[0]:
            for indicator, alert in alerts.items():
                self.alerts_queue.put({indicator: alert})
            full_alert_data['time'] = ticker_data[ticker_name]['time'].time()
            self.alert_table = self.save_alert_data_to_df(self.alert_table, {ticker_name: full_alert_data}, ticker_name)
            # self.write_alert_data_to_csv(self.alert_file, {ticker_name: full_alert_data}, ticker_name)

        # all alerts together work as single condition
        elif self.alert_params['condition'] == ALERT_CONDITIONS[1]:
            if len(alerts) == len(self.indicator_alerts):
                msg = f"list_of_ind_values meets all alerts"
                self.alerts_queue.put({ticker_name: msg})
                self.alert_table = self.save_alert_data_to_df(self.alert_table, {ticker_name: {ticker_name: msg}},
                                                              ticker_name)
                # self.write_alert_data_to_csv(self.alert_file, {ticker_name: {ticker_name: msg}}, ticker_name)

        # list of lists with indicator groups that form multiple conditions
        else:
            # feature
            pass

    @staticmethod
    def init_alerts_file_path():
        """
        Create alerts file path when doesn't exist and create filename
        with name like the datetime as string
        """
        if not os.path.exists(ALERTS_FILE_PATH):
            os.makedirs(ALERTS_FILE_PATH)
        current_datetime = datetime.datetime.now().strftime("%Y-%d-%m_%H-%M")
        filename = f"alert_log_{current_datetime}.csv"
        file_path = os.path.join(ALERTS_FILE_PATH, filename)
        return file_path

    @staticmethod
    def create_csv_info_data(file_name, indicator_names, condition, indicator_alerts):
        """
        Create file info data depending on the condition
        """
        headers = ['ticker_name']
        # current_alert_columns = [f"{indicator_names[indicator_idx]}" for indicator_idx in indicator_alerts]
        current_alert_columns = [f"{indicator_idx}" for indicator_idx in indicator_alerts]
        if ALERT_CONDITIONS[0] == condition:
            headers.extend(current_alert_columns)
            headers.extend(['at_time'])
        elif ALERT_CONDITIONS[1] == condition:
            headers = ['ticker', 'alert_msg', 'at_time']
        with open(file_name, 'a') as csv_file:
            csv_writer = csv.writer(csv_file, lineterminator='\n')
            for indicator_idx in indicator_names:
                csv_writer.writerow([indicator_names[indicator_idx]])
            csv_writer.writerow(headers)

    @staticmethod
    def write_alert_data_to_csv(file_name, alerts_df):
        """Write dataframe with alerts to csv file"""
        alerts_df.to_csv(file_name, mode='a', header=False)

    @staticmethod
    def save_alert_data_to_df(alerts_df, alert_messages, ticker_name):
        """Add new row with alerts to alerts dataframe"""
        alerts_df = pd.concat([alerts_df, pd.DataFrame(alert_messages[ticker_name], index=[ticker_name])])
        return alerts_df

    @staticmethod
    def name_create(indicator, ind_param, index):
        """Create indicator name form indicator params"""
        win_size = f"{ind_param['win_size']} period " if 'win_size' in ind_param else ''
        regular_name = f"{indicator['name']} {win_size}{ind_param['field']} {ind_param['time_frame']};"
        if index:
            name_with_index = f"{index}: "
            regular_name = name_with_index + regular_name
        return regular_name

    def init_indicator_names_alerts_included(self, params):
        """Add all indicators with created names to indicator_names dict"""
        indicator_names = {}
        for idx, param in params.items():
            indicator = params[idx]
            alert = self.indicator_alerts.get(idx)
            if indicator['name'] != 'STD':
                indicator_names[idx] = self.name_create(indicator, indicator['params'], str(idx))
            elif indicator['name'] == 'STD':
                indicator_names[idx] = [f"{str(idx)}: {indicator['name']}"]
                ind_params = [indicator['params']['name_1'], indicator['params']['name_2']]
                for ind_param in ind_params:
                    indicator_names[idx].append(self.name_create(ind_param, ind_param['params'], None))
                indicator_names[idx] = ' '.join(indicator_names[idx])
            if alert:
                symbol = list(alert.keys())[0]
                value = alert[symbol]
                alert_name = f" Alert: indicator {symbol} {value}"
            indicator_names[idx] += alert_name
        return indicator_names


if __name__ == '__main__':
    pass
    # al_man = AlertManager(PARAMS['indicator_params'], PARAMS['alert_params'], [])
    # a = 5
