import time
import requests
import json
import pandas as pd
import copy
from project_constants import *
from sqlalchemy import create_engine

STRUCTURE_COPY = copy.deepcopy(STRUCTURE)


def get_bulk_information(api_key, exchange='NASDAQ', limit=500, offset=0):
    url = MAIN_URL + f'{exchange}?api_token={api_key}&offset={offset}&limit={limit}&fmt=json'
    response = requests.get(url)
    return json.loads(response.text)


def insert_bulk_information(data):
    for stocks_info in data.values():
        ticker = 'st_' + stocks_info['General']['Code']
        for table_name, dictt in stocks_info.items():
            if table_name not in SPECIAL_COLUMNS:
                if table_name != 'General':
                    STRUCTURE_COPY[table_name]['TickerID'].append(ticker)
                if table_name == 'General':
                    STRUCTURE_COPY[table_name]['asset_id'].append(ticker)
                for key, value in dictt.items():
                    STRUCTURE_COPY[table_name][key].append(value)
            else:
                for sub_table_name, sub_dictt in dictt.items():
                    STRUCTURE_COPY[table_name][sub_table_name]['TickerID'].append(ticker)
                    for key, value in sub_dictt.items():
                        if type(value) == dict:
                            value = json.dumps(value)  # transform dict into json
                        STRUCTURE_COPY[table_name][sub_table_name][key].append(value)


def big_dick_algorithm():
    for exchange in EXCHANGES:
        print(exchange)
        limit = 500
        offset = 0
        data = get_bulk_information(EOD_API_KEY, exchange, limit, offset)
        insert_bulk_information(data)
        counter = 0
        while True:
            print(counter)
            counter += 1
            offset += limit
            data = get_bulk_information(EOD_API_KEY, exchange, limit, offset)
            if data == {}:
                break
            insert_bulk_information(data)


def transform_into_dfs():
    df_dict = {
        'general': pd.DataFrame(STRUCTURE_COPY['General']),
        'highlights': pd.DataFrame(STRUCTURE_COPY['Highlights']),
        'valuations': pd.DataFrame(STRUCTURE_COPY['Valuation']),
        'technicals': pd.DataFrame(STRUCTURE_COPY['Technicals']),
        'splits_dividends': pd.DataFrame(STRUCTURE_COPY['SplitsDividends']),
        'earnings_last_0': pd.DataFrame(STRUCTURE_COPY['Earnings']['Last_0']),
        'earnings_last_1': pd.DataFrame(STRUCTURE_COPY['Earnings']['Last_1']),
        'earnings_last_2': pd.DataFrame(STRUCTURE_COPY['Earnings']['Last_2']),
        'earnings_last_3': pd.DataFrame(STRUCTURE_COPY['Earnings']['Last_3']),
        'financials_balance_sheet': pd.DataFrame(STRUCTURE_COPY['Financials']['Balance_Sheet']),
        'financials_cash_flow': pd.DataFrame(STRUCTURE_COPY['Financials']['Cash_Flow']),
        'financials_income_statement': pd.DataFrame(STRUCTURE_COPY['Financials']['Income_Statement']),
    }
    return df_dict


def insert_into_sql_workbench(databases):
    my_conn = create_engine('mysql+mysqlconnector://root:MySQLka4anikli469@127.0.0.1:3306/usering')
    # databases['general'].to_sql('general', con=my_conn, if_exists='append', index=False)
    # databases['valuations'].to_sql('valuations', con=my_conn, if_exists='append', index=False)
    for name, db in databases.items():
        db.to_sql(name, con=my_conn, if_exists='append', index=False)


if __name__ == '__main__':
    start = time.time()
    big_dick_algorithm()
    print(time.time() - start)
    databases = transform_into_dfs()
    # insert_into_sql_workbench(databases)

    my_conn = create_engine('mysql+mysqlconnector://root:MySQLka4anikli469@127.0.0.1:3306/usering')

    old_df = pd.read_sql_table(
        'earning',
        con=my_conn
    )

    new_df = databases['general'].sort_values('asset_id').reset_index(drop=True)

    old_df.set_index('asset_id', inplace=True)
    new_df.set_index('asset_id', inplace=True)
    result = old_df == new_df
    b = result[result == False].stack().index.tolist()

    a = 0
