import copy
import datetime
import time, json

import mysql.connector
import pandas as pd
import threading, requests
import warnings

warnings.filterwarnings("ignore")

API_KEY = '8d42ff09a07eb4660de571b13ce8a786'
URL = 'https://financialmodelingprep.com/api/v3/quote/'
crypto_url = f'https://financialmodelingprep.com/api/v3/quotes/crypto?apikey={API_KEY}'

RES = []


def get_data_from_sql(number, crypto=False):
    l = threading.Lock()
    limit = 2000
    if crypto:
        query = """SELECT Symbol, Name, CoinName, Description, ImageUrl
                       FROM crypto_fundamentals.crypto_assets
                       LIMIT {} OFFSET {};""".format(limit, limit * number)
        database_connection = mysql.connector.connect(
            host="database-1.clns6yopmify.us-east-1.rds.amazonaws.com",
            user="admin",
            password="dsj89jdj!li3dj2ljefds",
            database='crypto_fundamentals'
        )
    else:
        database_connection = mysql.connector.connect(
            host="database-1.clns6yopmify.us-east-1.rds.amazonaws.com",
            user="admin",
            password="dsj89jdj!li3dj2ljefds",
            database='stock_etf_fundamentals'
        )
        query = """SELECT general.asset_id, general.Code, general.Name, general.Description, logos.LogoURL
                           FROM stock_etf_fundamentals.general
                           INNER JOIN stock_etf_fundamentals.logos ON general.asset_id=logos.TickerID
                           LIMIT {} OFFSET {};
                           """.format(limit, limit * number)
    my_cursor = database_connection.cursor(buffered=True)
    l.acquire()
    my_cursor.execute(query)
    l.release()
    result = my_cursor.fetchall()
    RES.extend(result)


start = time.time()
threads = []
for idx in range(5):
    x = threading.Thread(target=get_data_from_sql, args=(idx, True,))
    threads.append(x)
    x.start()
for idx in range(14):
    x = threading.Thread(target=get_data_from_sql, args=(idx,))
    threads.append(x)
    x.start()

for single_thread in threads:
    single_thread.join()

print(time.time() - start)
RES = pd.DataFrame(RES, columns=['asset_id', 'symbol', 'name', 'description', 'logo_url'])
RES['description'] = RES['description'].apply(lambda x: x.split('.')[0])
RES['class'] = 'stock'
RES.loc[RES['asset_id'].apply(lambda x: x.split('_')[0]) == 'et', 'class'] = 'etf'
RES.loc[RES['asset_id'].apply(lambda x: x.split('_')[0]) == 'cr', 'class'] = 'crypto'
URL_RES = []


def get_additional_data(tickers, crypto=False):
    if crypto:
        url = crypto_url
    else:
        url = copy.deepcopy(URL)
        for ticker in tickers:
            url += ticker + ','
        url = url[:-1]
        url += '?apikey='
        url += API_KEY
    l = threading.Lock()
    l.acquire()
    resp = requests.get(url)
    l.release()
    result = json.loads(resp.text)
    URL_RES.extend(result)


stock_etf_tickers = list(RES.loc[RES['class'] != 'crypto']['symbol'])
url_threads = []
x = threading.Thread(target=get_additional_data, args=([], True,))
url_threads.append(x)
x.start()
for idx in range(25):
    tickers = stock_etf_tickers[idx * 1000:(idx + 1) * 1000]
    x = threading.Thread(target=get_additional_data, args=(tickers,))
    url_threads.append(x)
    x.start()

for single_thread in url_threads:
    single_thread.join()

listt = []
print(time.time() - start)
now = datetime.datetime.now()


def insert_additional_fields(items):
    for item in items:
        ticker_symbol = item['symbol']
        if ticker_symbol in RES['symbol'].values:
            price = item['price']
            per_change = item['changesPercentage']
            m_cap = item['marketCap']
            vol = item['volume']
            avg_vol = item['avgVolume']
            if not avg_vol == 0 and vol is not None and avg_vol is not None:
                vol_flag = True if vol / avg_vol > 2 else False
            else:
                vol_flag = None
            earnings_date = item['earningsAnnouncement']
            if earnings_date is not None:
                earnings_date = datetime.datetime.strptime(earnings_date.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                earn_soon = True if (now + datetime.timedelta(days=3) >= earnings_date >= now) else False
            else:
                earn_soon = None
            # startt = time.time()
            listt.append([ticker_symbol, price, per_change, m_cap, vol_flag, earn_soon])
            # print(time.time() - startt)


additional_fields_threads = []
add_limit = 1000
for idx in range(16):
    values = URL_RES[idx * add_limit: (idx + 1) * add_limit]
    x = threading.Thread(target=insert_additional_fields, args=(values,))
    additional_fields_threads.append(x)
    x.start()

for thread in additional_fields_threads:
    thread.join()

B = RES.merge(pd.DataFrame(listt,
                           columns=['symbol', 'price', 'price change percentage', 'marketcap', 'unusual volume flag',
                                    'earnings coming up']), on='symbol', how='left')
print(time.time() - start)
a = 0

#  global lock
#  sql in one go
#  dynamic length
#  main script - coordinator
#  separate files fo each threading
