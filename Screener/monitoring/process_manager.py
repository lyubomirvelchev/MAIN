import collections
import json
import multiprocessing as mp
import time

import pandas as pd

from polygon import WebSocketClient, STOCKS_CLUSTER

from monitoring.monitoring_constants import EVENT_TYPE_SEC, EVENT_TYPE_MIN
from monitoring.utils import default_to_regular


TICKER_LIST = ['A.AMZN', 'A.AAPL']


class SocketMonitor:

    """
    Class initialize multiprocessing queue, that serves as buffer
    and start socket monitoring process
    """
    def __init__(self, tickers, api_key):
        self.raw_queue = mp.Queue()
        self.message_queue = mp.Queue()
        self.api_key = api_key
        self.socket_monitor = mp.Process(
            target=self.tickers_monitor, args=(
                self.raw_queue, self.api_key,
                self.get_socket_tickers(tickers, EVENT_TYPE_SEC, EVENT_TYPE_MIN), self.message_queue, self.terminate_process))

    # def __del__(self):
    #     self.socket_monitor.terminate()

    @staticmethod
    def get_socket_tickers(tickers, *event_type):
        """Add to every ticker in ticker list event type (A- second data , AM - minute)"""
        tickers_list = []
        for event in event_type:
            tickers_list.extend([f"{event}." + ticker for ticker in tickers])

        return tickers_list

    @staticmethod
    def tickers_monitor(queue, api_key, tickers, message_queue, on_close):
        """create web socket client and add queue filling method"""
        def update_queue(message):
            queue.put(message)
        my_client = WebSocketClient(STOCKS_CLUSTER, api_key, update_queue, on_close=on_close)
        my_client.run_async()
        my_client.subscribe(*tickers)
        if message_queue.get() == 'stop':
            """Access to my client !"""
            a = 5
            print("I am here")
            # my_client.subscribe(*TICKER_LIST)
            my_client.close_connection()

            print("We did it!")
            time.sleep(2)
            return

    def run_and_listen(self):
        """Starts monitoring process"""
        self.socket_monitor.start()

    def terminate_process(self):
        """Starts monitoring process"""
        self.socket_monitor.terminate()

class AggregateCalculator:
    """
    Class get messages from the raw queue,
    aggregate seconds data,
    and put the seconds and minute data to second and minute queue
    """
    def __init__(self, raw_queue, fields=['c', 'o', 'h', 'l', 'v', 'vw']):
        self.raw_queue = raw_queue
        self.aggr_sec_queue = mp.Queue()
        self.minute_queue = mp.Queue()
        self.aggregate_process = mp.Process(
            target=self.aggregate,
            args=(self.raw_queue, self.aggr_sec_queue, self.minute_queue, fields))
        self.aggregate_process.start()

    @staticmethod
    def aggregate(raw_queue, aggregate_second_queue, minute_queue, fields):
        next_time_frame_start = pd.to_datetime(0, unit='ms')
        output_msg = collections.defaultdict(lambda: dict({"s": next_time_frame_start},
                                                          **{fld: 0 for fld in fields}))
        while True:
            while not raw_queue.empty():
                messages = raw_queue.get()
                for msg in json.loads(messages):
                    minute_output_msg = {}

                    if msg['ev'] == EVENT_TYPE_MIN:
                        """
                        put in the minute queue dictionary with key ticker name with
                        values pandas data frame with timestamp as
                        index and ticker data as columns  
                        """
                        time_stamp = pd.to_datetime(msg['s'], unit='ms')
                        data = {'o': msg['o'], 'h': msg['h'], 'l': msg['l'],
                                'c': msg['c'], 'v': msg['v'], 'vw': msg['vw']}
                        minute_output_msg[msg['sym']] = pd.DataFrame(data, index=[time_stamp], columns=data)
                        minute_queue.put(minute_output_msg)

                    if msg['ev'] == EVENT_TYPE_SEC:
                        """
                       put in the seconds queue dictionary with key ticker name with
                       values pandas data frame with timestamp as
                       index and aggregate ticker data as columns  
                       """
                        current_time = pd.to_datetime(msg['s'], unit='ms')
                        current_minute = current_time.floor('min')
                        if next_time_frame_start < current_minute:
                            next_time_frame_start = current_minute
                            output_msg = collections.defaultdict(lambda: dict({"s": next_time_frame_start},
                                                                              **{fld: 0 for fld in fields}))

                        for field in fields:
                            if field == 'o' and output_msg[msg['sym']]['o'] == 0:
                                output_msg[msg['sym']][field] = msg[field]

                            elif field == 'h' and output_msg[msg['sym']]['h'] < msg['h']:
                                output_msg[msg['sym']][field] = msg[field]

                            elif field == 'l' and (output_msg[msg['sym']]['l'] > msg['l'] or output_msg[msg['sym']]['l'] == 0):
                                output_msg[msg['sym']][field] = msg[field]

                            elif field == 'c':
                                output_msg[msg['sym']][field] = msg[field]

                            elif field == 'v':
                                output_msg[msg['sym']][field] += msg[field]

                            elif field == 'vw':
                                output_msg[msg['sym']][field] = msg[field]

                        output_msg[msg['sym']]['s'] = current_time
                        aggregate_second_queue.put(default_to_regular({msg['sym']: output_msg[msg['sym']]}))


if __name__ == "__main__":
    mp.set_start_method('spawn')

    socket = SocketMonitor(TICKER_LIST)
    socket.run_and_listen()

    s = AggregateCalculator(socket.raw_queue)

    while True:
        print('start')
        print(s.aggr_sec_queue.get())