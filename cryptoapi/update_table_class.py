import requests

import pandas as pd
import numpy as np
import pprint
import copy
import json
from project_constants import *
from sqlalchemy import create_engine
from common_functions import transform_structure_dict_into_dfs, extract_full_market_data

STRUCTURE_COPY = copy.deepcopy(STRUCTURE)


class UpdateTables:
    def __init__(self, method, connection, db_name):
        self.connection_str = connection
        self.database_name = db_name
        self.main_table_name = 'general'
        self.db_connection = create_engine(self.connection_str + '/' + self.database_name)
        new_data = method(STRUCTURE_COPY)
        if not new_data:
            print('An error has occurred!')
        else:
            self.new_tables = transform_structure_dict_into_dfs(new_data)
            self.table_names = list(self.new_tables.keys())
            self.old_tables = self.get_tables_from_sql()
            self.compare_tables()
            pprint.pprint(self.tickers_to_be_updated)
            self.delete_delisted_tickers()
            tickers = list(set(self.tickers_to_insert + self.tickers_to_be_updated[self.main_table_name]))
            self.execute_insert_query_multiple_tickers(self.main_table_name, tickers)
            self.table_names.remove(self.main_table_name)
            for table_name in self.table_names:
                tickers = list(set(self.tickers_to_insert + self.tickers_to_be_updated[table_name]))
                self.execute_insert_query_multiple_tickers(table_name, tickers)

    def execute_insert_query_multiple_tickers(self, table_name, tickers):
        if len(tickers) < MAX_NUMBER_OF_TICKERS_PER_QUERY:
            self.construct_insert_on_duplicate_sql_query(table_name, tickers)
            return
        else:
            self.construct_insert_on_duplicate_sql_query(table_name, tickers[:MAX_NUMBER_OF_TICKERS_PER_QUERY])
            tickers = tickers[MAX_NUMBER_OF_TICKERS_PER_QUERY:]
            self.execute_insert_query_multiple_tickers(table_name, tickers)

    def get_tables_from_sql(self):
        dictt = {}
        for table_name in self.table_names:
            table = pd.read_sql_table(
                table_name,
                con=self.db_connection
            )
            table = table.drop(columns=['ID']) if 'ID' in table.columns else table
            dictt[table_name] = table
        return dictt

    def compare_tables(self):
        new_tickers = self.new_tables[self.main_table_name]
        old_tickers = self.old_tables[self.main_table_name]
        self.tickers_to_insert, self.tickers_to_delete = self.check_new_old_tickers(new_tickers, old_tickers)
        self.tickers_to_be_updated = {}
        for table_name in self.table_names:
            new_df, old_df = self.reformat_dataframes(self.new_tables[table_name], self.old_tables[table_name],
                                                      table_name)
            if 'UpdatedAt' in new_df.columns:
                new_df.drop(['UpdatedAt'], axis=1, inplace=True)
                old_df.drop(['UpdatedAt'], axis=1, inplace=True)
            if new_df.shape != old_df.shape:
                raise ArithmeticError
            if 'financials' in table_name:
                new_df = self.transform_financial_data_into_json(new_df)
            self.tickers_to_be_updated[table_name] = self.find_tickers_with_changed_values(new_df, old_df)

    @staticmethod
    def find_tickers_with_changed_values(new_df, old_df):
        differences_table = new_df == old_df
        both_nan_values = pd.isnull(new_df).replace(False, np.nan) == pd.isnull(old_df).replace(False, np.nan)
        table_with_differences = differences_table == both_nan_values
        idx_col_with_differences = table_with_differences[table_with_differences == True].stack().index.tolist()
        unique_tickers_to_be_updated = set([tpl[0] for tpl in idx_col_with_differences])
        return list(unique_tickers_to_be_updated)

    def construct_insert_on_duplicate_sql_query(self, table_name, tickers_to_be_changed):
        print(len(tickers_to_be_changed))
        if len(tickers_to_be_changed) == 0:
            return
        table = self.new_tables[table_name]
        columns = list(table.columns)
        insert_sql_query = f'INSERT INTO {self.database_name}.{table_name} ('
        for column in columns:
            insert_sql_query += column
            insert_sql_query += ', '
        insert_sql_query = insert_sql_query[:-2]
        insert_sql_query += ') VALUES ('
        for ticker in list(tickers_to_be_changed):
            values = table.loc[table['TickerID'] == ticker].values[0] if table_name != self.main_table_name else \
                table.loc[table['asset_id'] == ticker].values[0]
            for value in values:
                if pd.isnull(value):
                    insert_sql_query += f'NULL, '
                elif type(value) == str:
                    value = value.replace("'", "''")
                    insert_sql_query += f'\'{value}\', '
                else:
                    insert_sql_query += f'{value}, '
            insert_sql_query = insert_sql_query[:-2]
            insert_sql_query += '), ('
        insert_sql_query = insert_sql_query[:-3]
        insert_sql_query += ' ON DUPLICATE KEY UPDATE '
        for column in columns:
            insert_sql_query += f'{column} = VALUES({column})'
            insert_sql_query += ', '
        insert_sql_query = insert_sql_query[:-2]
        insert_sql_query += ';'
        self.db_connection.execute(insert_sql_query)
        print(table_name + ' updated!')

    def reformat_dataframes(self, new_df, old_df, table_name):
        index_column = 'asset_id' if table_name == self.main_table_name else 'TickerID'
        new_df = new_df.set_index(index_column).sort_index()
        old_df = old_df.set_index(index_column).sort_index()
        new_df.drop(self.tickers_to_insert, inplace=True)
        old_df.drop(self.tickers_to_delete, inplace=True)
        return new_df, old_df

    @staticmethod
    def check_new_old_tickers(new_data, old_data):
        new_tickers = list(new_data['asset_id'].values)
        old_tickers = list(old_data['asset_id'].values)
        tickers_to_insert = set(new_tickers) - set(old_tickers)
        tickers_to_delete = set(old_tickers) - set(new_tickers)
        return list(tickers_to_insert), list(tickers_to_delete)

    def delete_delisted_tickers(self):
        if not self.tickers_to_delete:
            return
        delete_sql_query = 'DELETE FROM {}.general WHERE asset_id IN ('.format(self.database_name)
        for ticker in self.tickers_to_delete:
            delete_sql_query += '\'{}\', '.format(ticker)
        delete_sql_query = delete_sql_query[:-2]
        delete_sql_query += ');'
        self.db_connection.execute(delete_sql_query)
        print("Deleted")
        print(self.tickers_to_delete)

    @staticmethod
    def get_ticker_logo(ticker):
        url = f'https://eodhistoricaldata.com/api/fundamentals/{ticker}?api_token={EOD_API_KEY}&filter=General'
        response = requests.get(url)
        if response.status_code == 200:
            json_obj = json.loads(response.text)
            try:
                logo_url = json_obj['General']['LogoURL']
            except KeyError:
                return 'st_' + ticker, None
            if logo_url == '':
                return 'st_' + ticker, None
            return 'st_' + ticker, 'https://eodhistoricaldata.com' + logo_url
        else:
            print(response)
            return 'st_' + ticker, None

    def insert_logos_in_db(self):
        ticker_log_tuples = []
        for ticker in self.tickers_to_insert:
            ticker_log_tuples.append(self.get_ticker_logo(ticker))
        insert_sql_query = f'INSERT INTO {db_name}.logos (TickerID, LogoUrl) VALUES '
        for values in ticker_log_tuples:
            insert_sql_query += f'(\'{values[0]}\', \'{values[1]}\'),' \
                if values[1] is not None else f'(\'{values[0]}\', NULL),'
        insert_sql_query = insert_sql_query[:-1]
        insert_sql_query += ';'
        self.db_connection.execute(insert_sql_query)
        print('Ticker logos updated!')

    @staticmethod
    def transform_financial_data_into_json(new_data):
        columns = list(new_data.columns)
        for col in columns[1:]:
            new_data[col] = new_data[col].apply(json.loads)
        return new_data


if __name__ == '__main__':
    connection = 'mysql+mysqlconnector://root:MySQLka4anikli469@127.0.0.1:3306'
    db_name = 'full_data'
    a = UpdateTables(extract_full_market_data, connection, db_name)
