import copy
import time

from project_constants import *
from sqlalchemy import create_engine
from common_functions import transform_structure_dict_into_dfs, extract_full_market_data, create_empty_tables

STRUCTURE_COPY = copy.deepcopy(STRUCTURE)


def insert_into_sql(databases, connection_str, database_name):
    engine = create_engine(connection_str + '/' + database_name)
    for name, db in databases.items():
        db.to_sql(name, con=engine, if_exists='append', index=False)


def create_populate_new_database(connection_str, database_name):
    create_empty_tables(connection_str, database_name)
    new_data = extract_full_market_data(STRUCTURE_COPY)
    if not new_data:
        print('An error has occurred!')
        return False
    dataframes = transform_structure_dict_into_dfs(new_data)
    insert_into_sql(dataframes, connection_str, database_name)


if __name__ == '__main__':
    connection = 'mysql+mysqlconnector://root:MySQLka4anikli469@127.0.0.1:3306'
    db_name = 'full_data'
    start = time.time()
    create_populate_new_database(connection, db_name)
    print(time.time() - start)
