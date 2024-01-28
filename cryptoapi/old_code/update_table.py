import pandas as pd
import numpy as npp
import copy
from project_constants import *
from sqlalchemy import create_engine
from common_functions import transform_structure_dict_into_dfs, extract_full_ticker_data

STRUCTURE_COPY = copy.deepcopy(STRUCTURE)


def get_tables_from_sql(connection_str, keys, database_name):
    conn = create_engine(connection_str + '/' + database_name)
    dictt = {}
    for table_name in keys:
        table = pd.read_sql_table(
            table_name,
            con=conn
        )
        table = table.drop(columns=['ID']) if 'ID' in table.columns else table
        dictt[table_name] = table
    return dictt


def whole_algorithm(connection_str, database_name):
    new_data = extract_full_ticker_data(STRUCTURE_COPY)
    new_databases = transform_structure_dict_into_dfs(new_data)
    db_names = list(new_databases.keys())
    old_tables = get_tables_from_sql(connection_str, db_names, database_name)
    tickers_to_insert, tickers_to_delete = check_new_old_tickers(new_databases['general'], old_tables['general'])
    for table_name in db_names:
        new_df, old_df = refactor_dataframes(new_databases[table_name], old_tables[table_name], table_name)
        if new_df.shape != old_df.shape:
            raise ArithmeticError
        differences_table = new_df == old_df
        both_nan_values = pd.isnull(new_df).replace(False, npp.nan) == pd.isnull(old_df).replace(False, npp.nan)
        table_with_differences = differences_table == both_nan_values
        b = table_with_differences[table_with_differences == True].stack().index.tolist()
        print(b)

def refactor_dataframes(new_df, old_df, table_name):
    index_column = 'asset_id' if table_name == 'general' else 'TickerID'
    new_df.set_index(index_column, inplace=True).sort_index(inplace=True)
    old_df.set_index(index_column, inplace=True).sort_index(inplace=True)
    new_df.drop(tickers_to_insert, inplace=True)
    old_df.drop(tickers_to_delete, inplace=True)

def check_new_old_tickers(new_data, old_data):
    new_tickers = list(new_data['asset_id'].values)
    old_tickers = list(old_data['asset_id'].values)
    tickers_to_insert = set(new_tickers) - set(old_tickers)
    tickers_to_delete = set(old_tickers) - set(new_tickers)
    return list(tickers_to_insert), list(tickers_to_delete)


if __name__ == '__main__':
    connection = 'mysql+mysqlconnector://root:MySQLka4anikli469@127.0.0.1:3306'
    db_name = 'stockfundamentals'
    whole_algorithm(connection, db_name)
