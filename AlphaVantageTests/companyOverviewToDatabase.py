# Code used from ChatGPT, then modified to fit our needs

# Imports
import json
import sqlite3
import os
from ticker_dictionary_file import ticker_dictionary

# Constant Variables
OUTPUT_FILE = './stock_data.db'
COMPANY_INFO_TABLE_NAME = 'CompanyInfo'
COMPANY_HISTORICAL_TABLE_NAME = 'CompanyHistorical'
COMPANY_FINANCIALS_TABLE_NAME =  'CompanyFinancials'
STOCK_TABLE_NAME = 'Stock'

# All the ticker names to be used for getting files
all_tickers = list(ticker_dictionary.keys())

# Check if the database file exists
if not os.path.exists(OUTPUT_FILE):
    print("Error: Database file not found. Exiting.")
    exit()

# Connect to SQLite database (create it if not exists)
conn = sqlite3.connect(OUTPUT_FILE)
cursor = conn.cursor()


# Company Info population

# Check if the table exists
cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{COMPANY_INFO_TABLE_NAME}'")
existing_table = cursor.fetchone()

if not existing_table:
    print(f"Error: Table '{COMPANY_INFO_TABLE_NAME}' does not exist. Skipping...")
    pass
else:
    # Put daily information into database
    for ticker in all_tickers:

        filepath = ('./' + ticker + '_company_overview.json')

        try:
            # Load JSON data from file
            with open(filepath, 'r') as file:
                json_data = json.load(file)
        except FileNotFoundError:
            print("Error: File " + filepath + " not found.")
            continue

        # Extract relevant information
        try:
            company_cik             = int(json_data['CIK'])
            asset_type              = json_data['AssetType']
            currency                = json_data['Currency']
            country                 = json_data['Country']
            address                 = json_data['Address']
            fiscal_year_end         = json_data['FiscalYearEnd']
            latest_quarter          = json_data['LatestQuarter']
            market_capitalization   = int(json_data['MarketCapitalization'])
            description             = json_data['Description']

            # Insert into single table
            cursor.execute(f'''
                INSERT OR IGNORE INTO {COMPANY_INFO_TABLE_NAME} (company_cik, asset_type, currency, country, address, fiscal_year_end, latest_quarter, market_capitalization, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (company_cik, asset_type, currency, country, address, fiscal_year_end, latest_quarter, market_capitalization, description))
        except KeyError as e:
            print(f"KeyError: {e} in {filepath} Skipping file...")
            continue

    conn.commit()



# Company Historical population

# Check if the table exists
cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{COMPANY_HISTORICAL_TABLE_NAME}'")
existing_table = cursor.fetchone()

if not existing_table:
    print(f"Error: Table '{COMPANY_HISTORICAL_TABLE_NAME}' does not exist. Skipping...")
    pass
else:
    # Put daily information into database
    for ticker in all_tickers:

        filepath = ('./' + ticker + '_company_overview.json')

        try:
            # Load JSON data from file
            with open(filepath, 'r') as file:
                json_data = json.load(file)
        except FileNotFoundError:
            print("Error: File " + filepath + " not found.")
            continue

        # Extract relevant information
        try:
            stock_id                        = int(ticker_dictionary[ticker])
            cik                             = int(json_data['CIK'])
            ebitda                          = int(json_data['EBITDA'])
            dividend_per_share              = float(json_data['DividendPerShare'])
            divident_yield                  = float(json_data['DividendYield'])
            revenue_per_share_ttm           = float(json_data['RevenuePerShareTTM'])
            profit_margin                   = float(json_data['ProfitMargin'])
            operating_margin_ttm            = float(json_data['OperatingMarginTTM'])
            return_on_assets_ttm            = float(json_data['ReturnOnAssetsTTM'])
            return_on_equity_ttm            = float(json_data['ReturnOnEquityTTM'])
            revenue_ttm                     = int(json_data['RevenueTTM'])
            gross_profit_ttm                = int(json_data['GrossProfitTTM'])
            diluted_eps_ttm                 = float(json_data['DilutedEPSTTM'])
            quarterly_earnings_growth_yoy   = float(json_data['QuarterlyEarningsGrowthYOY'])
            quarterly_revenue_growth_yoy    = float(json_data['QuarterlyRevenueGrowthYOY'])
            trailing_pe                     = float(json_data['TrailingPE'])
            price_to_sales_ration_ttm       = float(json_data['PriceToSalesRatioTTM'])
            price_to_book_ratio             = float(json_data['PriceToBookRatio'])
            fiftytwo_week_high              = float(json_data['52WeekHigh'])
            fiftytwo_week_low               = float(json_data['52WeekLow'])
            dividend_date                   = json_data['DividendDate']
            ex_divident_date                = json_data['ExDividendDate']

            # Insert into single table
            cursor.execute(f'''
                INSERT OR IGNORE INTO {COMPANY_HISTORICAL_TABLE_NAME} (stock_id, cik, ebitda, dividend_per_share, divident_yield, revenue_per_share_ttm, profit_margin, operating_margin_ttm, return_on_assets_ttm, return_on_equity_ttm, revenue_ttm, gross_profit_ttm, diluted_eps_ttm, quarterly_earnings_growth_yoy, quarterly_revenue_growth_yoy, trailing_pe, price_to_sales_ration_ttm, price_to_book_ratio, fiftytwo_week_high, fiftytwo_week_low, dividend_date, ex_divident_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (stock_id, cik, ebitda, dividend_per_share, divident_yield, revenue_per_share_ttm, profit_margin, operating_margin_ttm, return_on_assets_ttm, return_on_equity_ttm, revenue_ttm, gross_profit_ttm, diluted_eps_ttm, quarterly_earnings_growth_yoy, quarterly_revenue_growth_yoy, trailing_pe, price_to_sales_ration_ttm, price_to_book_ratio, fiftytwo_week_high, fiftytwo_week_low, dividend_date, ex_divident_date))
        except KeyError as e:
            print(f"KeyError: {e} in {filepath} Skipping file...")
            continue

    conn.commit()


# Commit the changes and close the connection
conn.commit()
conn.close()
