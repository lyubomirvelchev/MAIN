import time

import requests
import json
import pandas as pd
import copy
from project_constants import *
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, JSON, BigInteger, Integer, String, MetaData, ForeignKey, Float, DECIMAL


def create_forex_tables(connection_str, database_name):
    metadata = MetaData()

    forex = Table(
        'forex',
        metadata,
        Column('asset_id', String(15), primary_key=True),
        Column('symbol', String(15)),
        Column('name', String(80)),
    )

    forex_pairs = Table(
        'forex_pairs',
        metadata,
        Column('asset_id', String(15), primary_key=True),
        Column('symbol', String(15)),
        Column('currency_group', String(40)),
        Column('currency_base', String(40)),
        Column('currency_quote', String(40)),
    )

    indices = Table(
        'indices',
        metadata,
        Column('asset_id', String(25), primary_key=True),
        Column('symbol', String(15)),
        Column('name', String(80)),
        Column('country', String(40)),
        Column('currency', String(20)),
    )

    engine = create_engine(connection_str + '/' + database_name)
    metadata.create_all(engine)


if __name__ == '__main__':
    connection = 'mysql+mysqlconnector://admin:dsj89jdj!li3dj2ljefds@database-1.clns6yopmify.us-east-1.rds.amazonaws.com:3306'
    # connection = 'mysql+mysqlconnector://root:MySQLka4anikli469@127.0.0.1:3306'
    db_name = 'forex_indices_fundamentals'
    create_forex_tables(connection, db_name)
