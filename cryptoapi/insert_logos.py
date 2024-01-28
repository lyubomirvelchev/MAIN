import json, time
import multiprocessing

import requests
import pandas as pd
from project_constants import *
from sqlalchemy import create_engine, Integer, String, MetaData, Column, Table, ForeignKey


def get_tickers_in_db(connection_str, database_name):
    connection = create_engine(connection_str + '/' + database_name)
    table = pd.read_sql_table('general', con=connection)
    tickers = list(table['Code'].values)
    return tickers, connection


# def get_ticker_logo(ticker):
#     url = f'https://eodhistoricaldata.com/api/fundamentals/{ticker}?api_token={EOD_API_KEY}&filter=General'
#     response = requests.get(url)
#     if response.status_code == 200:
#         json_obj = json.loads(response.text)
#         try:
#             logo_url = json_obj['LogoURL']
#         except (KeyError, TypeError):
#             return 'st_' + ticker, None
#         if logo_url == '':
#             return 'st_' + ticker, None
#         return 'st_' + ticker, 'https://eodhistoricaldata.com' + logo_url
#     else:
#         print(response)
#         return 'st_' + ticker, None

def create_dataframe_with_logos(tickers):
    df = pd.DataFrame(columns=['TickerID', 'LogoUrl'])
    for idx in range(len(tickers)):
        print(idx)
        ticker = tickers[idx]
        logo_url = get_ticker_logo(ticker)
        ticker_id = 'st_' + ticker
        df.loc[idx] = [ticker_id, logo_url]
    return df




if __name__ == '__main__':
    connection = 'mysql+mysqlconnector://root:MySQLka4anikli469@127.0.0.1:3306'
    db_name = 'try_logos'
    tickers, connection = get_tickers_in_db(connection, db_name)
    df = create_dataframe_with_logos(tickers)
    # insert_logos_in_db(connection, df, db_name)
    counter = 0
    tickers = tickers[MAX_NUMBER_OF_TICKERS_PER_QUERY * 13:]
    while len(tickers) > MAX_NUMBER_OF_TICKERS_PER_QUERY:
        print(counter)
        ticker_logo_tuples = logos_with_pool(tickers[:MAX_NUMBER_OF_TICKERS_PER_QUERY])
        print('Logos gotten')
        insert_logos_in_db(connection, ticker_logo_tuples, db_name)
        print('Logos inserted')
        tickers = tickers[MAX_NUMBER_OF_TICKERS_PER_QUERY:]
        counter += MAX_NUMBER_OF_TICKERS_PER_QUERY
    ticker_logo_tuples = logos_with_pool(tickers)
    insert_logos_in_db(connection, ticker_logo_tuples, db_name)
    b = 0
