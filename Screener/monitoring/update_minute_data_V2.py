import datetime
import pandas as pd
import numpy as np

from screen.enum_data.enum_obj import DailyFields, TimeFrames


class UpdateMinuteDataV2:

    @staticmethod
    def get_last_minute_data(field, tickers_dict, timestamp, previous_data):
        # TODO: Test!
        return pd.DataFrame(
            data={k: v[field].values for k, v in tickers_dict.items()},
            index=[timestamp],
            columns=[t for t in previous_data.columns])

    @staticmethod
    def aggregate_minute_data(field, tickers, previous_data, time_frame, last_minute_aggr):
        for ticker in tickers:
            prev_ticker_data = previous_data[field][time_frame][ticker].iloc[-1]
            last_min_agg_data = last_minute_aggr[ticker].iloc[0]
            if field == 'close':
                prev_ticker_data = last_min_agg_data
            elif field == "high":
                current_high = last_min_agg_data
                previous_high = prev_ticker_data
                if current_high > previous_high or np.isnan(previous_high):
                    prev_ticker_data = current_high
            elif field == "low":
                current_min = last_min_agg_data
                previous_min = prev_ticker_data
                if current_min < previous_min or np.isnan(previous_min):
                    prev_ticker_data = current_min
            elif field == "open":
                current_open = last_min_agg_data
                if np.isnan(prev_ticker_data):
                    prev_ticker_data = current_open
            elif field == "volume":
                current_volume = last_min_agg_data
                if np.isnan(prev_ticker_data):
                    prev_ticker_data = 0
                if np.isnan(current_volume):
                    current_volume = 0
                prev_ticker_data += current_volume
            elif field == "vwap":
                prev_ticker_data = last_min_agg_data

            previous_data[field][time_frame][ticker].iloc[-1] = prev_ticker_data

    @staticmethod
    def get_tickers_queue_data(minute_queue):
        current_time_stamp = None
        tickers_dict = {}
        while not minute_queue.empty():
            msg = minute_queue.get()
            print(msg)
            ticker, ticker_df = msg.popitem()
            current_time_stamp = ticker_df.index[0]
            if current_time_stamp not in tickers_dict:
                tickers_dict[current_time_stamp] = {}
            tickers_dict[current_time_stamp][ticker] = ticker_df
        return tickers_dict, current_time_stamp + datetime.timedelta(minutes=1)

    @staticmethod
    def get_prev_data_keys(previous_data):
        return [(field, time_frame) for field in previous_data for time_frame in previous_data[field]]

    @staticmethod
    def add_new_row(prev_data, new_data):
        return pd.concat([prev_data, new_data])

    def update_time_frames_data_V2(self, previous_data, minute_queue):
        modified_time_frames = []
        tickers_queue_data, current_time = self.get_tickers_queue_data(minute_queue)
        prev_data_keys = self.get_prev_data_keys(previous_data)
        for field, time_frame in prev_data_keys:
            for timestamp in tickers_queue_data:
                last_minute_data = self.get_last_minute_data(DailyFields[field].value, tickers_queue_data[timestamp],
                                                             timestamp, previous_data[field][time_frame])

                last_index = previous_data[field][time_frame].index[-1]
                module_number = timestamp.minute % TimeFrames[time_frame].value
                expected_label = timestamp - datetime.timedelta(minutes=module_number)

                if (timestamp.minute + 1) % TimeFrames[time_frame].value == 0 and expected_label == last_index:
                    """Closing the aggregate"""
                    if timestamp in previous_data[field][time_frame].index:
                        continue

                    if TimeFrames[time_frame].name == '1min':
                        previous_data[field][time_frame] = self.add_new_row(previous_data[field][time_frame],
                                                                            last_minute_data)

                        modified_time_frames.append(time_frame)
                        continue
                    else:
                        self.aggregate_minute_data(field, tickers_queue_data[timestamp].keys(), previous_data, time_frame,
                                                   last_minute_data)

                        modified_time_frames.append(time_frame)
                    continue

                if timestamp.minute % TimeFrames[time_frame].value == 0:
                    if timestamp in previous_data[field][time_frame].index:
                        continue

                    previous_data[field][time_frame] = self.add_new_row(previous_data[field][time_frame],
                                                                        last_minute_data)
                    continue

                if expected_label != last_index and expected_label not in previous_data[field][time_frame].index:
                    last_minute_data = self.get_last_minute_data(DailyFields[field].value,
                                                                 tickers_queue_data[timestamp],
                                                                 expected_label, previous_data[field][time_frame])
                    """Generate leftover timestamp"""

                    previous_data[field][time_frame] = self.add_new_row(previous_data[field][time_frame],
                                                                        last_minute_data)
                    continue

                self.aggregate_minute_data(field, tickers_queue_data[timestamp].keys(), previous_data, time_frame,
                                           last_minute_data)
            print(previous_data[field][time_frame].tail(10))
        # if datetime.datetime.now().minute == 28:
        #     for field, time_frame in all_df:
        #         print(previous_data[field][time_frame].tail(20))
        modified_time_frames = list(dict.fromkeys(modified_time_frames))
        return modified_time_frames, current_time.minute


if __name__ == '__main__':
    ...

    # new added
    # def update_time_frames_data(self, prime_data, time_frames):
    #     time_frame_data = {}
    #     for time_frame in time_frames:
    #         if self.current_time is not None and (self.current_time.minute + 1) % TIME_FRAMES[time_frame] == 0:
    #             tickers = {}
    #             time_stamp_indices = None
    #             for ticker in prime_data:
    #                 time_stamp_indices = [
    #                     self.current_time - datetime.timedelta(minutes=t) for t in range(TIME_FRAMES[time_frame])]
    #                 idx_filter = prime_data[ticker].index.isin(time_stamp_indices)
    #                 data = prime_data[ticker].loc[idx_filter]
    #                 if not data.empty:
    #                     tickers[ticker] = self.aggregate_data(data)
    #             time_frame_data[time_frame] = {time_stamp_indices[-1] + datetime.timedelta(
    #                 minutes=TIME_FRAMES[time_frame]): tickers} if time_frame != '1min' else {
    #                 time_stamp_indices[-1]: tickers}
    #     return time_frame_data

# def update_time_frames_data_new(self, previous_data, minute_queue):
#     modified_time_frames = []
#     tickers_dict = self.get_tickers_dict_data(minute_queue)
#     all_df = self.get_all_df(previous_data)
#
#     for field, time_frame in all_df:
#         for timestamp in tickers_dict:
#             print('')
#             print(timestamp)
#             print('')
#             last_minute_aggr = self.get_last_minute_aggr_df(DailyFields[field].value, tickers_dict[timestamp],
#                                                             timestamp, previous_data[field][time_frame])
#             if (timestamp.minute + 1) % TimeFrames[time_frame].value == 0:
#                 if timestamp in previous_data[field][time_frame].index:
#                     continue
#
#                 if TimeFrames[time_frame].name == '1min':
#                     print('')
#                     print('one minute update')
#                     print('')
#                     print('last minute', last_minute_aggr)
#                     print('before update', previous_data[field][time_frame].tail(2))
#
#                     previous_data[field][time_frame] = pd.concat(
#                         [previous_data[field][time_frame], last_minute_aggr])
#
#                     modified_time_frames.append(time_frame)
#
#                     print('one minute update', previous_data[field][time_frame].tail(2))
#                     print('')
#                     continue
#
#                 print('')
#                 print('aggregate before time frame is ready')
#                 print('')
#                 print('last minute before ready', last_minute_aggr)
#                 print('')
#                 self.aggregate_minute_data(field, tickers_dict[timestamp].keys(), previous_data, time_frame,
#                                            last_minute_aggr)
#
#                 modified_time_frames.append(time_frame)
#
#                 print('ready timeframe data',previous_data[field][time_frame].tail(2))
#                 print('')
#                 continue
#
#             if timestamp.minute % TimeFrames[time_frame].value == 0:
#                 if timestamp in previous_data[field][time_frame].index:
#                     continue
#                 print('')
#                 print('append new row')
#                 print('')
#
#                 print('last minute before append new row', last_minute_aggr)
#
#                 previous_data[field][time_frame] = pd.concat(
#                     [previous_data[field][time_frame], last_minute_aggr])
#
#                 print('')
#                 print('after append', previous_data[field][time_frame].tail(2))
#                 print('')
#                 continue
#
#             last_index = previous_data[field][time_frame].index[-1]
#             module_number = timestamp.minute % TimeFrames[time_frame].value
#             last_label = timestamp - datetime.timedelta(minutes=module_number)
#             if last_label != last_index and not last_label in previous_data[field][time_frame].index:
#                 last_minute_aggr = self.get_last_minute_aggr_df(DailyFields[field].value, tickers_dict[timestamp],
#                                                                 last_label, previous_data[field][time_frame])
#
#                 previous_data[field][time_frame] = pd.concat(
#                     [previous_data[field][time_frame], last_minute_aggr])
#
#                 print('')
#                 print('!!!!!!!!create new row !!!!!')
#                 print('')
#                 print('last minute before create new row', last_minute_aggr)
#                 print('after create new row', previous_data[field][time_frame].tail(2))
#                 continue
#
#             print('')
#             print('aggregate data')
#             print('')
#             print('aggregate min data', last_minute_aggr)
#             print('')
#             print('before aggregate', previous_data[field][time_frame].tail(2))
#             print('')
#             self.aggregate_minute_data(field, tickers_dict[timestamp].keys(), previous_data, time_frame,
#                                        last_minute_aggr)
#
#             print(time_frame, field)
#             print('after aggregate', previous_data[field][time_frame].tail(2))
#             print('')
#     return modified_time_frames
