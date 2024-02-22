# Imports
import json
import sqlite3

# Constant Variables
OUTPUT_FILE = './stock_data.db'

# Connect to SQLite database (create it if not exists)
conn = sqlite3.connect(OUTPUT_FILE)
cursor = conn.cursor()

# Create a table for TimeSeriesData
cursor.execute('''

    CREATE TABLE IF NOT EXISTS TimeSeriesData (
        stock_id INT,
        symbol TEXT,
        date DATETIME,
        open DOUBLE,
        high DOUBLE,
        low DOUBLE,
        close DOUBLE,
        volume INT,
        PRIMARY KEY (stock_id, date)
    )
''')

# Create a table for CompanyInfo
cursor.execute('''

    CREATE TABLE IF NOT EXISTS CompanyInfo (
        company_cik INT,
        assest_type VARCHAR(45),
        currency VARCHAR(45),
        country VARCHAR(45),
        address VARCHAR(90),
        fiscal_year_end VARCHAR(45),
        latest_quarter VARCHAR(45),
        markey_capitalization INT,
        descriotion VARCHAR(6000),
        PRIMARY KEY (company_cik)
    )
''')

# Create a table for CompanyHistorical
cursor.execute('''

    CREATE TABLE IF NOT EXISTS CompanyHistorical (
        stock_id INT,
        cik INT,
        ebitda INT,
        dividend_per_share DOUBLE,
        divident_yield DOUBLE,
        revenue_per_share DOUBLE,
        profit_margin DOUBLE,
        operating_margin_ttm DOUBLE,
        return_on_assets_ttm DOUBLE,
        return_on_equity_ttm DOUBLE,
        revenue_ttm INT,
        gross_profit_ttm INT,
        diluted_eps_ttm DOUBLE,
        quarterly_earnings_growth_yoy DOUBLE,
        quarterly_revenue_growth_yoy DOUBLE,
        trailing_pe DOUBLE,
        price_to_sales_ration_ttm DOUBLE,
        price_to_book_ratio DOUBLE,
        fiftytwo_week_high DOUBLE,
        fiftytwo_week_low DOUBLE,
        dividend_date DATE,
        ex_divident_date DATE,
        PRIMARY KEY (stock_id, cik)
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
