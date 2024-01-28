import concurrent.futures
import datetime
import pandas as pd
import pytz
import tqdm

from polygon import RESTClient

from filters.filters_constants import SUMMER_TIME_PRE_MARKET_HOURS_RANGE, SUMMER_TIME_MARKET_HOURS_RANGE, \
    WINTER_TIME_PRE_MARKET_HOURS_RANGE, WINTER_TIME_MARKET_HOURS_RANGE, API_KEY
from screen.enum_data import DailyFields, ComparisonOperators

TICKER_LIST = ['AA', 'AAIC', 'AAT', 'ABM', 'ACBI', 'ACHV', 'ACIW', 'ACM', 'ACN', 'ACST', 'ACTG', 'ADC', 'ADP', 'AEIS',
               'AESE', 'AEY', 'AFAC', 'AFIN', 'AGCB', 'AGO', 'AHPI', 'AIMC', 'AIR', 'AJRD', 'AL', 'ALEX', 'ALIT', 'ALK',
               'ALRM', 'ALSA', 'ALX', 'AMAL', 'AMAT', 'AMH', 'AMKR', 'AMPI', 'AMS', 'AMT', 'ANSS', 'AON', 'APD', 'APG',
               'APH', 'APLE', 'APR', 'APSG', 'ARCC', 'ARDX', 'AROC', 'ARTW', 'ASAX', 'ASIX', 'ATC', 'ATEC', 'ATVI',
               'AUTO', 'AVGO', 'AY', 'AYI', 'AZPN', 'BAC', 'BAFN', 'BALY', 'BAM', 'BANC', 'BANX', 'BBQ', 'BC', 'BCAC',
               'BCO', 'BCRX', 'BCSA', 'BCSF', 'BELFB', 'BERY', 'BFAM', 'BGS', 'BH', 'BHAT', 'BKCC', 'BKNG', 'BLK',
               'BMBL', 'BMY', 'BNL', 'BOKF', 'BON', 'BRG', 'BRKR', 'BROG', 'BRPM', 'BRQS', 'BSGA', 'BSVN', 'BV', 'BWA',
               'BWFG', 'CAAP', 'CAH', 'CATO', 'CBOE', 'CCBG', 'CCLP', 'CCTS', 'CDNS', 'CGBD', 'CHDN', 'CHEF', 'CHMI',
               'CHW', 'CIEN', 'CIO', 'CIXX', 'CKPT', 'CLAQ', 'CLBK', 'CLDT', 'CLH', 'CLPR', 'CMCL', 'CMRX', 'CND',
               'CNDA', 'CNHI', 'CNM', 'CNO', 'CNSL', 'CNXN', 'CODX', 'COHR', 'COO', 'CPA', 'CR', 'CRD.A', 'CRD.B',
               'CSCW', 'CSR', 'CTGO', 'CTIB', 'CTKB', 'CTS', 'CTT', 'CTVA', 'CTXR', 'CUBA', 'CUBI', 'CUEN', 'CUZ',
               'CVET', 'CVGI', 'CYAN', 'DAN', 'DARE', 'DBD', 'DCI', 'DEA', 'DHIL', 'DLB', 'DLNG', 'DLPN', 'DLR', 'DLX',
               'DNLI', 'DOGZ', 'DPRO', 'EAC', 'ECL', 'ECOR', 'ELS', 'ELY', 'EMBK', 'EMN', 'EMP', 'EMX', 'ENS', 'ENVB',
               'EPAY', 'EPRT', 'EQ', 'EQC', 'EQIX', 'ESBA', 'ESBK', 'ESGR', 'ESSA', 'ETD', 'EVFM', 'EXLS', 'EXN',
               'EXPO', 'FA', 'FARO', 'FCF', 'FCNCA', 'FCPT', 'FCRD', 'FDP', 'FELE', 'FERG', 'FFIV', 'FKWL', 'FLIC',
               'FNF', 'FPAC', 'FPH', 'FRC', 'FRT', 'FSP', 'FSV', 'FULT', 'FUND', 'FXCO', 'G', 'GAMC', 'GAPA', 'GBX',
               'GDEV', 'GEF.B', 'GILT', 'GLRE', 'GMED', 'GNCA', 'GNL', 'GOOD', 'GORO', 'GRBK', 'GSBC', 'GTES', 'GTPA',
               'GWII', 'H', 'HAAC', 'HAPP', 'HCCI', 'HCKT', 'HCWB', 'HEPA', 'HERA', 'HILS', 'HIW', 'HLIO', 'HLT',
               'HNRG', 'HOFT', 'HPLT', 'HPX', 'HRTG', 'HSIC', 'HSII', 'HST', 'HTGC', 'HUBB', 'HUGS', 'HUN', 'HXL',
               'ICAD', 'ICHR', 'IEP', 'IFF', 'IKT', 'IMV', 'INAQ', 'INFO', 'INTE', 'INVE', 'INVO', 'IONS', 'IP', 'IPAX',
               'IQMD', 'IR', 'IRIX', 'IRM', 'IROQ', 'IRWD', 'ISAA', 'ITCI', 'ITT', 'JAN', 'JBGS', 'JBL', 'JEF', 'JELD',
               'JLL', 'KELYA', 'KEX', 'KFRC', 'KFY', 'KIM', 'KIRK', 'KLAC', 'KMI', 'KOSS', 'KRBP', 'KRO', 'KSCP', 'KSI',
               'KVSC', 'KWR', 'LAMR', 'LEA', 'LECO', 'LION', 'LNC', 'LOB', 'LOCL', 'LOCO', 'LOW', 'LPG', 'LSEA', 'LUCD',
               'LW', 'MAIN', 'MAR', 'MAT', 'MAYS', 'MCAE', 'MCAF', 'MCB', 'MDRR', 'MEI', 'MFC', 'MGA', 'MGP', 'MHK',
               'MIDD', 'MIND', 'MINM', 'MKSI', 'MMC', 'MN', 'MNST', 'MNTN', 'MO', 'MOTV', 'MPW', 'MPX', 'MRC', 'MRCC',
               'MRIN', 'MRK', 'MS', 'MSA', 'MSAC', 'MSDA', 'MSFT', 'MTG', 'MTN', 'MTVC', 'MX', 'MYGN', 'NATI', 'NBIX',
               'NCSM', 'NDAQ', 'NDSN', 'NEOG', 'NEP', 'NETC', 'NEWT', 'NGD', 'NKE', 'NLIT', 'NLOK', 'NLSN', 'NLSP',
               'NMFC', 'NMRK', 'NN', 'NNN', 'NP', 'NRIX', 'NSTS', 'NUZE', 'NVEE', 'NVST', 'NVT', 'NWL', 'NWS', 'NX',
               'NXGL', 'NXGN', 'NYMT', 'OBT', 'OCDX', 'OCSL', 'ODC', 'OGS', 'OLN', 'OLP', 'OMQS', 'OPK', 'OPOF', 'ORCC',
               'ORI', 'OXSQ', 'PACK', 'PAHC', 'PATI', 'PBIP', 'PCCT', 'PCOM', 'PDCO', 'PEPL', 'PESI', 'PFLT', 'PHVS',
               'PIRS', 'PKBK', 'PLAB', 'PLXS', 'PNFP', 'PNNT', 'POLY', 'PRA', 'PRAA', 'PRGS', 'PRI', 'PRO', 'PTMN',
               'PVL', 'PYCR', 'QGEN', 'RACE', 'RBA', 'RBKB', 'RCI', 'RDN', 'REG', 'REPH', 'RGA', 'RGP', 'RKDA', 'RLI',
               'RMBS', 'RMR', 'RNER', 'ROCR', 'ROG', 'ROL', 'RPT', 'RRGB', 'RXRA', 'SAMA', 'SBAC', 'SBR', 'SCHN', 'SCM',
               'SCPS', 'SFE', 'SGBX', 'SGII', 'SIER', 'SII', 'SITC', 'SLNH', 'SLVR', 'SMED', 'SMIH', 'SMLP', 'SNAX',
               'SNFCA', 'SNII', 'SNTG', 'SNV', 'SPG', 'SPGI', 'SPNT', 'SQL', 'SRAX', 'SRC', 'SSB', 'SSBI', 'SSSS',
               'SSY', 'STAG', 'STE', 'STIM', 'STLA', 'STOR', 'STX', 'SWKS', 'SYTA', 'TARO', 'TATT', 'TAYD', 'TBI',
               'TBK', 'TBPH', 'TENX', 'TFX', 'TG', 'TGB', 'THM', 'THMO', 'THO', 'TINV', 'TMX', 'TNC', 'TNDM', 'TNET',
               'TOI', 'TOMZ', 'TPB', 'TPX', 'TRC', 'TREC', 'TRKA', 'TRMB', 'TROW', 'TRU', 'TRUE', 'TSCO', 'TSEM',
               'TSLA', 'TSLX', 'TTC', 'TTMI', 'TTSH', 'TWNK', 'TXT', 'UBCP', 'UBFO', 'UEIC', 'UGI', 'UIHC', 'UMH',
               'USM', 'UTAA', 'UUU', 'VAQC', 'VBFC', 'VGFC', 'VHI', 'VHNA', 'VIAV', 'VICI', 'VIEW', 'VIGL', 'VII',
               'VPG', 'VRAY', 'VRNT', 'VSH', 'VTR', 'VTSI', 'VVV', 'VYNT', 'WALD', 'WBA', 'WHLR', 'WILC', 'WMPN', 'WMT',
               'WOR', 'WPC', 'WPCA', 'WRK', 'WSBC', 'WTT', 'WTW', 'XFIN', 'XPOA', 'YELP', 'YTEN', 'ZGNX', 'ZNGA']


class HourlyFilter:
    def __init__(self, tickers):
        self.tickers = tickers
        self.all_selected_tickers = self.get_aggregate_ticker_data()

    @staticmethod
    def summer_time_end_date(year):
        """
        Generate daylight saving time end date
        for selected year
        """
        month = 11
        day = 1
        current_date = datetime.date(year, month, day)
        first_w = current_date.isoweekday() - 1
        if first_w == 7:
            first_w = 0
        first_saturday = 7 - first_w

        return datetime.date(year, month, first_saturday)

    @staticmethod
    def summer_time_start_date(year):
        """
        Generate daylight saving time start date
        for selected year
        """
        month = 3
        day = 1
        date = datetime.date(year, month, day)
        first_w = date.isoweekday() - 1
        if first_w == 7:
            first_w = 0
        second_saturday = 14 - first_w
        return datetime.date(year, month, second_saturday)

    @staticmethod
    def is_day_monday(date):
        """Return if selected date day is monday"""
        return date.weekday() == 0

    def is_summer_time_period(self, current_date):
        """Returns if current date is in selected period(Summer Time)"""
        start_period = self.summer_time_start_date(current_date.year)
        end_period = self.summer_time_end_date(current_date.year)

        return start_period <= current_date.date() <= end_period

    def get_hours_range_period(self, date, pre_market):
        """Returns date in current time period with the type of market"""
        if self.is_summer_time_period(date):
            if pre_market:
                return SUMMER_TIME_PRE_MARKET_HOURS_RANGE
            return SUMMER_TIME_MARKET_HOURS_RANGE
        else:
            if pre_market:
                return WINTER_TIME_PRE_MARKET_HOURS_RANGE
            return WINTER_TIME_MARKET_HOURS_RANGE

    def get_today_and_previous_day(self):
        """Return the two needed dates to make request
         and create indices to tickers DataFrames"""

        today = datetime.datetime.now(tz=pytz.utc)
        today = today.replace(minute=0, second=0, microsecond=0)

        if self.is_day_monday(today):
            previous_day = today - datetime.timedelta(days=3)
        else:
            previous_day = today - datetime.timedelta(days=1)

        return today, previous_day

    def generate_market_timestamps(self, pre_market):
        """
        Returns trade period for two dates and selected premarket(bool)
        """

        today, previous_day = self.get_today_and_previous_day()
        dates = {
            'today': self.get_hours_range_period(today, pre_market),
            'previous_day': self.get_hours_range_period(previous_day, pre_market)
        }
        """Get the previous hour ticker data"""
        previous_hour = today - datetime.timedelta(hours=1)

        trade_period = []
        hour = previous_hour.hour
        """Check if hour is in today's selected range of hours 
            and append to trade_period list datetime.datetime
        """
        if hour in dates['today']:
            to_index = dates['today'].index(hour)
            """Get list slice of today date list from start to selected index"""
            today_hours = dates['today'][:to_index + 1]
            """Generate timestamps backward"""
            for i in range(len(today_hours) - 1, - 1, -1):
                timestamp = datetime.datetime(
                    year=today.year, month=today.month, day=today.day, hour=today_hours[i], minute=0, second=0)
                trade_period.append(timestamp)

        previous_hours = dates['previous_day']
        """Generate timestamps backward"""
        for j in range(len(previous_hours) - 1, -1, -1):
            """Handle the case when is summer time and hour is 0:00:00"""
            if previous_hours[j] == 24:
                d = (previous_day + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                timestamp = datetime.datetime(
                    year=d.year, month=previous_day.month, day=d.day, hour=0, minute=0,
                    second=0)
                trade_period.append(timestamp)
                continue
            timestamp = datetime.datetime(
                year=previous_day.year, month=previous_day.month, day=previous_day.day, hour=previous_hours[j],
                minute=0, second=0)
            trade_period.append(timestamp)

        return trade_period

    @staticmethod
    def make_request(args):
        with RESTClient(API_KEY) as client:
            response = client.stocks_equities_aggregates(*args)
            if response.queryCount:
                res = response.results
                return {'ticker': args[0], 'values': res}

    def get_aggregate_ticker_data(self):
        """
        Download minute data for self.tickers,
        convert the ticker data to pd.DataFrame
        and save it to all_selected_tickers as
        [ticker] = pd.DataFrame()

        returns all_selected_tickers dict
        """

        all_selected_tickers = {}
        today, previous_day = self.get_today_and_previous_day()
        today_str = today.strftime('%Y-%m-%d')
        previous_day_str = previous_day.strftime('%Y-%m-%d')
        map_params = [(t, 1, 'hour', previous_day_str, today_str) for t in TICKER_LIST]

        with concurrent.futures.ProcessPoolExecutor(max_workers=20) as executor:
            results = tqdm.tqdm(executor.map(self.make_request, map_params))
            for result in results:
                if result:
                    tickers_df = pd.DataFrame(result['values'])
                    tickers_df['t'] = pd.to_datetime(tickers_df['t'], unit='ms')
                    tickers_df.set_index('t', inplace=True)

                    all_selected_tickers[result['ticker']] = tickers_df
        return all_selected_tickers

    @staticmethod
    def get_indexed_df(df_data, timestamps):
        """returns pd.DataFrame
        with data indexed by selected timestamp
        """
        df = pd.DataFrame(index=timestamps, data=df_data)
        return df

    def get_sliced_needed_hours(self, df_data, hours_count, timestamps):
        """Returns DataFrame for the selected hours_count"""
        df = self.get_indexed_df(df_data, timestamps[::-1])
        """Asure that hours_count will be less or equal to the DataFrame length"""
        if len(df) < hours_count:
            hours_count = len(df)
        """get from the last to -hours_count rows"""
        selected_daily_period_data = df.loc[df.index[-hours_count:]]
        return selected_daily_period_data

    @staticmethod
    def compare_values(abs_value, compare_sign, abs_diff, percent, delimiter):
        """
        Returns compare(bool) that is product of the compare using
        ComparisonOperators.
        When abs_value is False the filtration is by absolute value change,
        and when is True the filtration is by percent_change.
        """
        if abs_value:
            compare = ComparisonOperators[compare_sign].value(abs_diff, percent)
        else:
            percent_change = (abs_diff / delimiter) * 100
            compare = ComparisonOperators[compare_sign].value(percent_change, percent)
        return compare

    def filter_by_PercentChange(
            self, hour_count, percent, field, compare_sign, pre_market=True, abs_value=False):
        """
        Filter data for selected period.
        When abs_value is False the filtration is by absolute value change,
        and when is True the filtration is by percent_change.
        When pre_market is False the filtration is by open market data,
        and when is True the filtration is by all premarket data.

        returns and modifies 'self.tickers't
        """
        tickers = []
        timestamps = self.generate_market_timestamps(pre_market)
        for ticker in self.tickers:
            if ticker in self.all_selected_tickers:
                df = self.get_sliced_needed_hours(self.all_selected_tickers[ticker], hour_count, timestamps)
                """Get the first and the last row values"""
                first_value = df.iloc[-1][DailyFields[field].value]
                last_value = df.iloc[0][DailyFields[field].value]

                abs_diff = first_value - last_value

                if self.compare_values(abs_value, compare_sign, abs_diff, percent, first_value):
                    tickers.append(ticker)

        self.tickers = tickers

        return self.tickers

    def filter_by_AverageChange(
            self, hour_count, percent, field, compare_sign, pre_market=True, abs_value=False):
        """
               Filter data for selected period.
               When abs_value is False the filtration is by absolute value change,
               and when is True the filtration is by percent_change.
               When pre_market is False the filtration is by open market data,
               and when is True the filtration is by all premarket data.

               returns and modifies 'self.tickers't
               """
        tickers = []
        timestamps = self.generate_market_timestamps(pre_market)
        for ticker in self.tickers:
            df = self.get_sliced_needed_hours(self.all_selected_tickers[ticker], hour_count, timestamps)
            avg_value = (df[DailyFields[field].value].sum()) / hour_count
            first_value = df.iloc[-1][DailyFields[field].value]
            abs_diff = first_value - avg_value

            if self.compare_values(abs_value, compare_sign, abs_diff, percent, avg_value):
                tickers.append(ticker)
        self.tickers = tickers
        return self.tickers

    def filter_by_AbsValue(
            self, value, field, compare_sign, pre_market=True):
        """
        Filter data for selected period by absolute value of the field.
        When pre_market is False the filtration is by open market data,
        and when is True the filtration is by all premarket data.

        returns and modifies 'self.tickers'
        """
        tickers = []
        timestamps = self.generate_market_timestamps(pre_market)
        for ticker in self.tickers:
            if ticker in self.all_selected_tickers:
                df = self.get_sliced_needed_hours(self.all_selected_tickers[ticker], 1, timestamps)
                """Get the first and the last row values"""
                from_time = df.iloc[-1][DailyFields[field].value]
                if ComparisonOperators[compare_sign].value(from_time, value):
                    tickers.append(ticker)

        self.tickers = tickers

        return self.tickers

if __name__ == "__main__":
    non_d_fr = HourlyFilter(TICKER_LIST)
    res = non_d_fr.filter_by_percent_change(5, -1.5, 'open', '<', abs_value=True)
    res2 = non_d_fr.filter_by_current_filed_values_to_average_field_value(5, 3, 'open', '<')
    res3 = non_d_fr.filter_by_absolute_field_value(20000, 'volume', ">", False)
    print(len(non_d_fr.tickers))