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
            company_cik = json_data['CIK']
            asset_type = json_data['AssetType']
            currency = json_data['Currency']
            country = json_data['Country']
            address = json_data['Address']
            fiscal_year_end = json_data['FiscalYearEnd']
            latest_quarter = json_data['LatestQuarter']
            market_capitalization = json_data['MarketCapitalization']
            description = json_data['Description']

            # Insert into single table
            cursor.execute(f'''
                INSERT OR IGNORE INTO {COMPANY_INFO_TABLE_NAME} (company_cik, asset_type, currency, country, address, fiscal_year_end, latest_quarter, market_capitalization, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (company_cik, asset_type, currency, country, address, fiscal_year_end, latest_quarter, market_capitalization, description))
        except KeyError as e:
            print(f"KeyError: {e} in {filepath} Skipping file...")
            continue


# Commit the changes and close the connection
conn.commit()
conn.close()
