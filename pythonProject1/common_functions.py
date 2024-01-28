import requests
import json
import pandas as pd
import copy
from project_constants import *
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, JSON, BigInteger, Integer, String, MetaData, ForeignKey, Float, DECIMAL


def get_all_etf_symbols():
    url = SYMBOL_LIST_URL + EOD_API_KEY + '&fmt=json'
    response = requests.get(url)
    json_obj = json.loads(response.text)
    exchanges = {}

    for ticker in json_obj:
        if ticker['Type'] == 'ETF':
            if ticker['Exchange'] not in exchanges.keys():
                exchanges[ticker['Exchange']] = [ticker['Code']]
            else:
                exchanges[ticker['Exchange']].append(ticker['Code'])
    exchanges['NYSE'].extend(exchanges['NYSE ARCA'] + exchanges['NYSE MKT'])
    return exchanges


def get_exchange_etf_data(exchange, tickers):
    url = MAIN_URL + exchange + '?&symbols='
    for ticker in tickers:
        url += ticker
        url += ','
    url = url[:-1]
    url += f'&api_token={EOD_API_KEY}&fmt=json'
    response = requests.get(url)
    return json.loads(response.text)


def extract_all_etf_data(structure_dict):
    etfs = get_all_etf_symbols()
    for exchange in EXCHANGES:
        print(exchange)
        if exchange in etfs.keys():
            tickers = etfs[exchange]
            counter = 1
            while True:
                if len(tickers) > 500:
                    data = get_exchange_etf_data(exchange, tickers[:500])
                    insert_bulk_information(data, structure_dict)
                    tickers = tickers[500:]
                else:
                    data = get_exchange_etf_data(exchange, tickers)
                    insert_bulk_information(data, structure_dict)
                    break
                print(counter)
                counter += 1
    return structure_dict


def get_bulk_information(api_key, exchange='NASDAQ', limit=500, offset=0):
    try:
        url = MAIN_URL + f'{exchange}?api_token={api_key}&offset={offset}&limit={limit}&fmt=json'
        response = requests.get(url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(response)
            return False
    except requests.exceptions.ConnectionError as e:
        print(e)
        print('No connection!')
        return False


def insert_bulk_information(data, structure_dict):
    for stocks_info in data.values():
        ticker = 'st_' + stocks_info['General']['Code']
        for table_name, dictt in stocks_info.items():
            used_columns = set()
            if table_name not in SPECIAL_COLUMNS:
                if table_name != 'General':
                    structure_dict[table_name]['TickerID'].append(ticker)
                if table_name == 'General':
                    structure_dict[table_name]['asset_id'].append(ticker)
                for key, value in dictt.items():
                    structure_dict[table_name][key].append(value)
                    used_columns.add(key)
                used_columns.add('asset_id') if table_name == 'General' else used_columns.add('TickerID')
                unupdated_keys = set(structure_dict[table_name].keys()) - used_columns
                for unupdated_value in unupdated_keys:
                    structure_dict[table_name][unupdated_value].append(None)

            else:
                for sub_table_name, sub_dictt in dictt.items():
                    structure_dict[table_name][sub_table_name]['TickerID'].append(ticker)
                    for key, value in sub_dictt.items():
                        if type(value) == dict:
                            value = json.dumps(value)  # transform dict into json
                        structure_dict[table_name][sub_table_name][key].append(value)
                        used_columns.add(key)
                    used_columns.add('TickerID')
                    unupdated_keys = set(structure_dict[table_name][sub_table_name].keys()) - used_columns
                    for unupdated_value in unupdated_keys:
                        structure_dict[table_name][sub_table_name][unupdated_value].append(None)


def extract_full_ticker_data(structure_dict):
    for exchange in EXCHANGES:
        print(exchange)
        limit = 500
        offset = 0
        counter = 0
        while True:
            data = get_bulk_information(EOD_API_KEY, exchange, limit, offset)
            if data == False:
                return False
            if data == {}:
                break
            insert_bulk_information(data, structure_dict)
            print(counter)
            counter += 1
            offset += limit
    return structure_dict


def transform_structure_dict_into_dfs(structure_dict, prefix=''):
    df_dict = {
        prefix + 'general': pd.DataFrame(structure_dict['General']),
        prefix + 'highlights': pd.DataFrame(structure_dict['Highlights']),
        prefix + 'valuations': pd.DataFrame(structure_dict['Valuation']),
        prefix + 'technicals': pd.DataFrame(structure_dict['Technicals']),
        prefix + 'splits_dividends': pd.DataFrame(structure_dict['SplitsDividends']),
        prefix + 'earnings_last_0': pd.DataFrame(structure_dict['Earnings']['Last_0']),
        prefix + 'earnings_last_1': pd.DataFrame(structure_dict['Earnings']['Last_1']),
        prefix + 'earnings_last_2': pd.DataFrame(structure_dict['Earnings']['Last_2']),
        prefix + 'earnings_last_3': pd.DataFrame(structure_dict['Earnings']['Last_3']),
        prefix + 'financials_balance_sheet': pd.DataFrame(structure_dict['Financials']['Balance_Sheet']),
        prefix + 'financials_cash_flow': pd.DataFrame(structure_dict['Financials']['Cash_Flow']),
        prefix + 'financials_income_statement': pd.DataFrame(structure_dict['Financials']['Income_Statement']),
    }
    return df_dict


def create_empty_tables(connection_str, database_name, prefix=''):
    metadata = MetaData()

    general = Table(
        prefix + 'general',
        metadata,
        Column('asset_id', String(15), primary_key=True),
        Column('Code', String(15)),
        Column('Type', String(40)),
        Column('Name', String(500)),
        Column('Exchange', String(10)),
        Column('CurrencyCode', String(15)),
        Column('CurrencyName', String(20)),
        Column('CurrencySymbol', String(10)),
        Column('CountryName', String(10)),
        Column('CountryISO', String(10)),
        Column('ISIN', String(40)),
        Column('CUSIP', String(40)),
        Column('Sector', String(40)),
        Column('Industry', String(500)),
        Column('Description', String(6000)),
        Column('FullTimeEmployees', DECIMAL(10, 0)),
        Column('UpdatedAt', String(15)),
    )

    highlights = Table(
        prefix + 'highlights',
        metadata,
        Column('ID', Integer, primary_key=True),
        Column('MarketCapitalization', DECIMAL(15, 0)),
        Column('MarketCapitalizationMln', DECIMAL(15, 5)),
        Column('EBITDA', DECIMAL(15, 0)),
        Column('PERatio', DECIMAL(15, 5)),
        Column('PEGRatio', DECIMAL(15, 5)),
        Column('WallStreetTargetPrice', DECIMAL(15, 5)),
        Column('BookValue', DECIMAL(15, 5)),
        Column('DividendShare', DECIMAL(15, 5)),
        Column('DividendYield', DECIMAL(10, 5)),
        Column('EarningsShare', DECIMAL(10, 5)),
        Column('EPSEstimateCurrentYear', DECIMAL(10, 5)),
        Column('EPSEstimateNextYear', DECIMAL(10, 5)),
        Column('EPSEstimateNextQuarter', DECIMAL(10, 5)),
        Column('MostRecentQuarter', String(30)),
        Column('ProfitMargin', DECIMAL(10, 5)),
        Column('OperatingMarginTTM', DECIMAL(10, 5)),
        Column('ReturnOnAssetsTTM', DECIMAL(10, 5)),
        Column('ReturnOnEquityTTM', DECIMAL(10, 5)),
        Column('RevenueTTM', DECIMAL(15, 0)),
        Column('RevenuePerShareTTM', DECIMAL(15, 5)),
        Column('QuarterlyRevenueGrowthYOY', DECIMAL(15, 5)),
        Column('GrossProfitTTM', DECIMAL(15, 0)),
        Column('DilutedEpsTTM', DECIMAL(15, 5)),
        Column('QuarterlyEarningsGrowthYOY', DECIMAL(15, 5)),
        Column('TickerID', String(15), ForeignKey(prefix + "general.asset_id", ondelete='CASCADE'),
               unique=True),

    )

    valuations = Table(
        prefix + 'valuations',
        metadata,
        Column('ID', Integer, primary_key=True),
        Column('TrailingPE', DECIMAL(12, 5)),
        Column('ForwardPE', DECIMAL(12, 5)),
        Column('PriceSalesTTM', DECIMAL(12, 5)),
        Column('PriceBookMRQ', DECIMAL(12, 5)),
        Column('EnterpriseValueRevenue', DECIMAL(12, 5)),
        Column('EnterpriseValueEbitda', DECIMAL(12, 5)),
        Column('TickerID', String(15), ForeignKey(prefix + "general.asset_id", ondelete='CASCADE'),
               unique=True),
    )

    technicals = Table(
        prefix + 'technicals',
        metadata,
        Column('ID', Integer, primary_key=True),
        Column('Beta', DECIMAL(10, 5)),
        Column('52WeekHigh', DECIMAL(12, 5)),
        Column('52WeekLow', DECIMAL(12, 5)),
        Column('50DayMA', DECIMAL(12, 5)),
        Column('200DayMA', DECIMAL(12, 5)),
        Column('SharesShort', DECIMAL(15, 0)),
        Column('SharesShortPriorMonth', DECIMAL(15, 0)),
        Column('ShortRatio', DECIMAL(12, 5)),
        Column('ShortPercent', DECIMAL(10, 5)),
        Column('TickerID', String(15), ForeignKey(prefix + "general.asset_id", ondelete='CASCADE'),
               unique=True),
    )

    splits_dividends = Table(
        prefix + 'splits_dividends',
        metadata,
        Column('ID', Integer, primary_key=True),
        Column('ForwardAnnualDividendRate', DECIMAL(10, 5)),
        Column('ForwardAnnualDividendYield', DECIMAL(10, 5)),
        Column('PayoutRatio', DECIMAL(10, 5)),
        Column('DividendDate', String(15)),
        Column('ExDividendDate', String(15)),
        Column('LastSplitFactor', String(15)),
        Column('LastSplitDate', String(15)),
        Column('TickerID', String(15), ForeignKey(prefix + "general.asset_id", ondelete='CASCADE'),
               unique=True),
    )

    earnings_last_0 = Table(
        prefix + 'earnings_last_0',
        metadata,
        Column('ID', Integer, primary_key=True),
        Column('date', String(15)),
        Column('epsActual', DECIMAL(10, 5)),
        Column('epsEstimate', DECIMAL(10, 5)),
        Column('epsDifference', DECIMAL(10, 5)),
        Column('surprisePercent', DECIMAL(25, 7)),
        Column('TickerID', String(15), ForeignKey(prefix + "general.asset_id", ondelete='CASCADE'),
               unique=True),
    )
    earnings_last_1 = Table(
        prefix + 'earnings_last_1',
        metadata,
        Column('ID', Integer, primary_key=True),
        Column('date', String(15)),
        Column('date', String(15)),
        Column('epsActual', DECIMAL(10, 5)),
        Column('epsEstimate', DECIMAL(10, 5)),
        Column('epsDifference', DECIMAL(10, 5)),
        Column('surprisePercent', DECIMAL(25, 7)),
        Column('TickerID', String(15), ForeignKey(prefix + "general.asset_id", ondelete='CASCADE'),
               unique=True),
    )
    earnings_last_2 = Table(
        prefix + 'earnings_last_2',
        metadata,
        Column('ID', Integer, primary_key=True),
        Column('date', String(15)),
        Column('date', String(15)),
        Column('epsActual', DECIMAL(10, 5)),
        Column('epsEstimate', DECIMAL(10, 5)),
        Column('epsDifference', DECIMAL(10, 5)),
        Column('surprisePercent', DECIMAL(25, 7)),
        Column('TickerID', String(15), ForeignKey(prefix + "general.asset_id", ondelete='CASCADE'),
               unique=True),
    )
    earnings_last_3 = Table(
        prefix + 'earnings_last_3',
        metadata,
        Column('ID', Integer, primary_key=True),
        Column('date', String(15)),
        Column('date', String(15)),
        Column('epsActual', DECIMAL(10, 5)),
        Column('epsEstimate', DECIMAL(10, 5)),
        Column('epsDifference', DECIMAL(10, 5)),
        Column('surprisePercent', DECIMAL(25, 7)),
        Column('TickerID', String(15), ForeignKey(prefix + "general.asset_id", ondelete='CASCADE'),
               unique=True),
    )

    financials_balance_sheet = Table(
        prefix + 'financials_balance_sheet',
        metadata,
        Column('ID', Integer, primary_key=True),
        Column('currency_symbol', String(10)),
        Column('quarterly_last_0', JSON),
        Column('quarterly_last_1', JSON),
        Column('quarterly_last_2', JSON),
        Column('quarterly_last_3', JSON),
        Column('yearly_last_0', JSON),
        Column('yearly_last_1', JSON),
        Column('yearly_last_2', JSON),
        Column('yearly_last_3', JSON),
        Column('TickerID', String(15), ForeignKey(prefix + "general.asset_id", ondelete='CASCADE'),
               unique=True),
    )

    financials_cash_flow = Table(
        prefix + 'financials_cash_flow',
        metadata,
        Column('ID', Integer, primary_key=True),
        Column('currency_symbol', String(10)),
        Column('quarterly_last_0', JSON),
        Column('quarterly_last_1', JSON),
        Column('quarterly_last_2', JSON),
        Column('quarterly_last_3', JSON),
        Column('yearly_last_0', JSON),
        Column('yearly_last_1', JSON),
        Column('yearly_last_2', JSON),
        Column('yearly_last_3', JSON),
        Column('TickerID', String(15), ForeignKey(prefix + "general.asset_id", ondelete='CASCADE'),
               unique=True),
    )
    financials_income_statement = Table(
        prefix + 'financials_income_statement',
        metadata,
        Column('ID', Integer, primary_key=True),
        Column('currency_symbol', String(10)),
        Column('quarterly_last_0', JSON),
        Column('quarterly_last_1', JSON),
        Column('quarterly_last_2', JSON),
        Column('quarterly_last_3', JSON),
        Column('yearly_last_0', JSON),
        Column('yearly_last_1', JSON),
        Column('yearly_last_2', JSON),
        Column('yearly_last_3', JSON),
        Column('TickerID', String(15), ForeignKey(prefix + "general.asset_id", ondelete='CASCADE'),
               unique=True),
    )

    engine = create_engine(connection_str + '/' + database_name)
    metadata.create_all(engine)
