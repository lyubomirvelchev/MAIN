import pandas as pd
from sqlalchemy import create_engine, MetaData

my_conn = create_engine('mysql+mysqlconnector://root:MySQLka4anikli469@127.0.0.1:3306/stockfundamentals')

table_df = pd.read_sql_table(
    'general',
    con=my_conn
)



a=0