import json
import time
import pandas as pd

import requests

API_KEY = '0075620F-AA4E-43F3-953F-309033B759FE'


def get_all_symbols(api_key):
    url = 'https://rest.coinapi.io/v1/symbols'
    headers = {'X-CoinAPI-Key': api_key}
    print('before_resp')
    response = requests.get(url, headers=headers)
    print('after_resp')
    return json.loads(response.text)


def get_latest_data(api_key, ticker, limit=100):
    url = 'https://rest.coinapi.io/v1/ohlcv/{}/latest?period_id=1MIN&limit={}'.format(ticker, limit)
    headers = {'X-CoinAPI-Key': api_key}
    response = requests.get(url, headers=headers)
    return json.loads(response.text)


def get_historical_data(api_key, ticker, time_start, limit=100):
    url = 'https://rest.coinapi.io/v1/ohlcv/{}/history?period_id=1MIN&time_start={}&limit={}'.format(ticker, time_start,
                                                                                                     limit)
    headers = {'X-CoinAPI-Key': api_key}
    response = requests.get(url, headers=headers)
    return json.loads(response.text)


if __name__ == '__main__':
    ticker_info = get_latest_data(API_KEY, 'KRAKENFTS_PERP_BTC_USD', limit=1000)
    print(ticker_info)
    print(len(ticker_info))
    ticker_info = get_historical_data(API_KEY, 'KRAKENFTS_PERP_BTC_USD', '2016-01-01T00:00:00', limit=1000)
    print(ticker_info)
    print(len(ticker_info))
    start = time.time()
    symbols_info = get_all_symbols(API_KEY)
    print(symbols_info)
    df = pd.DataFrame(columns=['symbol_id'])
    counter = 0
    for dictt in symbols_info[:10000]:
        df.loc[counter] = [dictt['symbol_id']]
        counter += 1
    print(time.time() - start)
    df.to_csv(r'C:\Users\user\PycharmProjects\cryptoapi\symbols.csv')
    print('Done')
