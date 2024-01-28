import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, JSON, BigInteger, Integer, String, MetaData, ForeignKey, Float

metadata = MetaData()


general = Table(
    'general',
    metadata,
    Column('asset_id', String(100), primary_key=True),
    Column('Code', String(100)),
    Column('Type', String(100)),
    Column('Name', String(1000)),
    Column('Exchange', String(100)),
    Column('CurrencyCode', String(100)),
    Column('CurrencyName', String(100)),
    Column('CurrencySymbol', String(100)),
    Column('CountryName', String(100)),
    Column('CountryISO', String(100)),
    Column('ISIN', String(100)),
    Column('CUSIP', String(100)),
    Column('Sector', String(100)),
    Column('Industry', String(100)),
    Column('Description', String(6000)),
    Column('FullTimeEmployees', Float),
    Column('UpdatedAt', String(100)),
)

highlights = Table(
    'highlights',
    metadata,
    Column('ID', Integer, primary_key=True),
    Column('MarketCapitalization', Float),
    Column('MarketCapitalizationMln', Float),
    Column('EBITDA', Float),
    Column('PERatio', Float),
    Column('PEGRatio', Float),
    Column('WallStreetTargetPrice', Float),
    Column('BookValue', Float),
    Column('DividendShare', Float),
    Column('DividendYield', Float),
    Column('EarningsShare', Float),
    Column('EPSEstimateCurrentYear', Float),
    Column('EPSEstimateNextYear', Float),
    Column('EPSEstimateNextQuarter', Float),
    Column('MostRecentQuarter', String(100)),
    Column('ProfitMargin', Float),
    Column('OperatingMarginTTM', Float),
    Column('ReturnOnAssetsTTM', Float),
    Column('ReturnOnEquityTTM', Float),
    Column('RevenueTTM', BigInteger),
    Column('RevenuePerShareTTM', Float),
    Column('QuarterlyRevenueGrowthYOY', Float),
    Column('GrossProfitTTM', Float),
    Column('DilutedEpsTTM', Float),
    Column('QuarterlyEarningsGrowthYOY', Float),
    Column('TickerID', String(100), ForeignKey("general.asset_id"), unique=True),

)

valuations = Table(
    'valuations',
    metadata,
    Column('ID', Integer, primary_key=True),
    Column('TrailingPE', Float),
    Column('ForwardPE', Float),
    Column('PriceSalesTTM', Float),
    Column('PriceBookMRQ', Float),
    Column('EnterpriseValueRevenue', Float),
    Column('EnterpriseValueEbitda', Float),
    Column('TickerID', String(100), ForeignKey("general.asset_id"), unique=True),
)

technicals = Table(
    'technicals',
    metadata,
    Column('ID', Integer, primary_key=True),
    Column('Beta', Float),
    Column('52WeekHigh', Float),
    Column('52WeekLow', Float),
    Column('50DayMA', Float),
    Column('200DayMA', Float),
    Column('SharesShort', Integer),
    Column('SharesShortPriorMonth', Integer),
    Column('ShortRatio', Float),
    Column('ShortPercent', Float),
    Column('TickerID', String(100), ForeignKey("general.asset_id"), unique=True),
)

splits_dividends = Table(
    'splits_dividends',
    metadata,
    Column('ID', Integer, primary_key=True),
    Column('ForwardAnnualDividendRate', Integer),
    Column('ForwardAnnualDividendYield', Float),
    Column('PayoutRatio', Float),
    Column('DividendDate', String(100)),
    Column('ExDividendDate', String(100)),
    Column('LastSplitFactor', String(100)),
    Column('LastSplitDate', String(100)),
    Column('TickerID', String(100), ForeignKey("general.asset_id"), unique=True),
)

earnings_last_0 = Table(
    'earnings_last_0',
    metadata,
    Column('ID', Integer, primary_key=True),
    Column('date', String(100)),
    Column('epsActual', Float),
    Column('epsEstimate', Float),
    Column('epsDifference', Float),
    Column('surprisePercent', Float),
    Column('TickerID', String(100), ForeignKey("general.asset_id"), unique=True),
)
earnings_last_1 = Table(
    'earnings_last_1',
    metadata,
    Column('ID', Integer, primary_key=True),
    Column('date', String(100)),
    Column('epsActual', Float),
    Column('epsEstimate', Float),
    Column('epsDifference', Float),
    Column('surprisePercent', Float),
    Column('TickerID', String(100), ForeignKey("general.asset_id"), unique=True),
)
earnings_last_2 = Table(
    'earnings_last_2',
    metadata,
    Column('ID', Integer, primary_key=True),
    Column('date', String(100)),
    Column('epsActual', Float),
    Column('epsEstimate', Float),
    Column('epsDifference', Float),
    Column('surprisePercent', Float),
    Column('TickerID', String(100), ForeignKey("general.asset_id"), unique=True),
)
earnings_last_3 = Table(
    'earnings_last_3',
    metadata,
    Column('ID', Integer, primary_key=True),
    Column('date', String(100)),
    Column('epsActual', Float),
    Column('epsEstimate', Float),
    Column('epsDifference', Float),
    Column('surprisePercent', Float),
    Column('TickerID', String(100), ForeignKey("general.asset_id"), unique=True),
)

financials_balance_sheet = Table(
    'financials_balance_sheet',
    metadata,
    Column('ID', Integer, primary_key=True),
    Column('currency_symbol', String(100)),
    Column('quarterly_last_0', JSON),
    Column('quarterly_last_1', JSON),
    Column('quarterly_last_2', JSON),
    Column('quarterly_last_3', JSON),
    Column('yearly_last_0', JSON),
    Column('yearly_last_1', JSON),
    Column('yearly_last_2', JSON),
    Column('yearly_last_3', JSON),
    Column('TickerID', String(100), ForeignKey("general.asset_id"), unique=True),
)

financials_cash_flow = Table(
    'financials_cash_flow',
    metadata,
    Column('ID', Integer, primary_key=True),
    Column('currency_symbol', String(100)),
    Column('quarterly_last_0', JSON),
    Column('quarterly_last_1', JSON),
    Column('quarterly_last_2', JSON),
    Column('quarterly_last_3', JSON),
    Column('yearly_last_0', JSON),
    Column('yearly_last_1', JSON),
    Column('yearly_last_2', JSON),
    Column('yearly_last_3', JSON),
    Column('TickerID', String(100), ForeignKey("general.asset_id"), unique=True),
)
financials_income_statement = Table(
    'financials_income_statement',
    metadata,
    Column('ID', Integer, primary_key=True),
    Column('currency_symbol', String(100)),
    Column('quarterly_last_0', JSON),
    Column('quarterly_last_1', JSON),
    Column('quarterly_last_2', JSON),
    Column('quarterly_last_3', JSON),
    Column('yearly_last_0', JSON),
    Column('yearly_last_1', JSON),
    Column('yearly_last_2', JSON),
    Column('yearly_last_3', JSON),
    Column('TickerID', String(100), ForeignKey("general.asset_id"), unique=True),
)

engine = create_engine('mysql+mysqlconnector://root:MySQLka4anikli469@127.0.0.1:3306/usering')
metadata.create_all(engine)
