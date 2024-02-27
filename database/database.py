import sqlite3

class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_db(self):
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        return db

    def close_db(self, db=None):
        if db is not None:
            db.close()

    def query_db(self, query, args=(), one=False):
        with self.get_db() as conn:
            cur = conn.cursor()
            cur.execute(query, args)
            rv = cur.fetchall()
            cur.close()
            return (rv[0] if rv else None) if one else rv

    def modify_db(self, query, args=()):
        with self.get_db() as conn:
            cur = conn.cursor()
            cur.execute(query, args)
            conn.commit()

    def init_db(self):
        with self.get_db() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS stock_prices (
                    symbol TEXT PRIMARY KEY, 
                    price TEXT, 
                    volume INTEGER, 
                    close_price REAL,
                    previous_close REAL,
                    last_updated DATETIME
                )''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS time_series (
                    symbol TEXT PRIMARY KEY, 
                    data TEXT, 
                    last_updated DATETIME
                )''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS company_overview (
                    Symbol TEXT PRIMARY KEY,
                    AssetType TEXT,
                    Name TEXT,
                    Description TEXT,
                    CIK TEXT,
                    Exchange TEXT,
                    Currency TEXT,
                    Country TEXT,
                    Sector TEXT,
                    Industry TEXT,
                    Address TEXT,
                    FiscalYearEnd TEXT,
                    LatestQuarter TEXT,
                    MarketCapitalization TEXT,
                    EBITDA TEXT,
                    PERatio TEXT,
                    PEGRatio TEXT,
                    BookValue TEXT,
                    DividendPerShare TEXT,
                    DividendYield TEXT,
                    EPS TEXT,
                    RevenuePerShareTTM TEXT,
                    ProfitMargin TEXT,
                    OperatingMarginTTM TEXT,
                    ReturnOnAssetsTTM TEXT,
                    ReturnOnEquityTTM TEXT,
                    RevenueTTM TEXT,
                    GrossProfitTTM TEXT,
                    DilutedEPSTTM TEXT,
                    QuarterlyEarningsGrowthYOY TEXT,
                    QuarterlyRevenueGrowthYOY TEXT,
                    AnalystTargetPrice TEXT,
                    AnalystRatingStrongBuy TEXT,
                    AnalystRatingBuy TEXT,
                    AnalystRatingHold TEXT,
                    AnalystRatingSell TEXT,
                    AnalystRatingStrongSell TEXT,
                    TrailingPE TEXT,
                    ForwardPE TEXT,
                    PriceToSalesRatioTTM TEXT,
                    PriceToBookRatio TEXT,
                    EVToRevenue TEXT,
                    EVToEBITDA TEXT,
                    Beta TEXT,
                    "52WeekHigh" TEXT,
                    "52WeekLow" TEXT,
                    "50DayMovingAverage" TEXT,
                    "200DayMovingAverage" TEXT,
                    SharesOutstanding TEXT,
                    DividendDate TEXT,
                    ExDividendDate TEXT,
                    last_updated DATETIME
                )''')

def get_database(db_path):
    return Database(db_path)

