import copy
from project_constants import *
from sqlalchemy import create_engine
from common_functions import transform_structure_dict_into_dfs, extract_full_ticker_data, extract_all_etf_data, \
    create_empty_tables

STRUCTURE_COPY = copy.deepcopy(STRUCTURE)


def insert_into_sql(databases, connection_str, database_name):
    engine = create_engine(connection_str + '/' + database_name)
    for name, db in databases.items():
        db.to_sql(name, con=engine, if_exists='append', index=False)


def create_populate_new_database(method, connection_str, database_name, etf=False):
    create_empty_tables(connection_str, database_name, prefix="etf_" if etf else '')
    new_data = method(STRUCTURE_COPY)
    if not new_data:
        print('An error has occurred!')
        return False
    dataframes = transform_structure_dict_into_dfs(new_data, prefix="etf_" if etf else '')
    insert_into_sql(dataframes, connection_str, database_name)


if __name__ == '__main__':
    connection = 'mysql+mysqlconnector://root:MySQLka4anikli469@127.0.0.1:3306'
    db_name = 'lambda_test'
    # etf_db_name = 'test_etfs'
    # create_populate_new_database(extract_all_etf_data, connection, etf_db_name, etf=True)
    create_populate_new_database(extract_full_ticker_data, connection, db_name)
