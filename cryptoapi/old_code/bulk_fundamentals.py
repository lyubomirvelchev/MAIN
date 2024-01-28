import requests
import json
import pandas as pd

EOD_API_KEY = '60941c62f10668.99813942'
EXCHANGES = ['NASDAQ', 'NYSE', 'BATS', 'AMEX']
MAIN_URL = 'http://eodhistoricaldata.com/api/bulk-fundamentals/'
SPECIAL_COLUMNS = ['Earnings', 'Financials']
DF_COLUMNS = ['Code', 'Type', 'Name', 'Exchange', 'CurrencyCode', 'CurrencyName', 'CurrencySymbol', 'CountryName',
              'CountryISO', 'ISIN', 'CUSIP', 'Sector', 'Industry', 'Description', 'FullTimeEmployees', 'UpdatedAt',
              'MarketCapitalization', 'MarketCapitalizationMln', 'EBITDA', 'PERatio', 'PEGRatio',
              'WallStreetTargetPrice', 'BookValue', 'DividendShare', 'DividendYield', 'EarningsShare',
              'EPSEstimateCurrentYear', 'EPSEstimateNextYear', 'EPSEstimateNextQuarter', 'MostRecentQuarter',
              'ProfitMargin', 'OperatingMarginTTM', 'ReturnOnAssetsTTM', 'ReturnOnEquityTTM', 'RevenueTTM',
              'RevenuePerShareTTM', 'QuarterlyRevenueGrowthYOY', 'GrossProfitTTM', 'DilutedEpsTTM',
              'QuarterlyEarningsGrowthYOY', 'TrailingPE', 'ForwardPE', 'PriceSalesTTM', 'PriceBookMRQ',
              'EnterpriseValueRevenue', 'EnterpriseValueEbitda', 'Beta', '52WeekHigh', '52WeekLow', '50DayMA',
              '200DayMA', 'SharesShort', 'SharesShortPriorMonth', 'ShortRatio', 'ShortPercent',
              'ForwardAnnualDividendRate', 'ForwardAnnualDividendYield', 'PayoutRatio', 'DividendDate',
              'ExDividendDate', 'LastSplitFactor', 'LastSplitDate']


def get_bulk_information(api_key, exchange='NASDAQ', limit=500, offset=0):
    url = MAIN_URL + f'{exchange}?api_token={api_key}&offset={offset}&limit={limit}&fmt=json'
    response = requests.get(url)
    return json.loads(response.text)


def get_columns(data):
    column_names = []
    kur = data['0']
    for name, dictt in kur.items():
        if name not in SPECIAL_COLUMNS:
            for key in dictt.keys():
                column_names.append(key)
    return column_names


def process_bulk_information(data):
    df_values = {col: [] for col in DF_COLUMNS}
    for single_stock in data.values():
        for name, dictt in single_stock.items():
            if name not in SPECIAL_COLUMNS:
                for key, value in dictt.items():
                    df_values[key].append(value)
    return pd.DataFrame(df_values).set_index('Code')


def combine_all_data_into_single_df():
    big_dick = pd.DataFrame()
    list_of_dfs = []
    for exchange in EXCHANGES:
        print(exchange)
        limit = 500
        offset = 0
        data = get_bulk_information(EOD_API_KEY, exchange, limit, offset)
        list_of_dfs.append(process_bulk_information(data))
        counter = 0
        while True:
            print(counter)
            counter += 1
            offset += limit
            data = get_bulk_information(EOD_API_KEY, exchange, limit, offset)
            if data == {}:
                break
            list_of_dfs.append(process_bulk_information(data))
    big_dick = big_dick.append(list_of_dfs)
    return big_dick


if __name__ == '__main__':
    # hui = get_bulk_information(EOD_API_KEY, EXCHANGES[1], 500, 0)
    # a = process_bulk_information(hui)
    a = combine_all_data_into_single_df()
    c = 0
