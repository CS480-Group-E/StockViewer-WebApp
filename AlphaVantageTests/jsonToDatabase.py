# Code used from ChatGPT, then modified to fit our needs

# Imports
import json
import sqlite3
import os
from ticker_dictionary_file import ticker_dictionary

# Constant Variables
OUTPUT_FILE = './stock_data.db'
TABLE_NAME = 'TimeSeriesData'

# All the ticker names to be used for getting files
all_tickers = list(ticker_dictionary.keys())

# Check if the database file exists
if not os.path.exists(OUTPUT_FILE):
    print("Error: Database file not found. Exiting.")
    exit()

# Connect to SQLite database (create it if not exists)
conn = sqlite3.connect(OUTPUT_FILE)
cursor = conn.cursor()

# Check if the table already exists
cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{TABLE_NAME}'")
existing_table = cursor.fetchone()

if not existing_table:
    print(f"Error: Table '{TABLE_NAME}' does not exist. Exiting...")
    conn.close()
    exit()

# Put daily information into database
for ticker in all_tickers:

    filepath = ('./' + ticker + '_daily.json')

    try:
        # Load JSON data from file
        with open(filepath, 'r') as file:
            json_data = json.load(file)
    except FileNotFoundError:
        print("Error: File " + filepath + " not found.")
        continue

    # Extract relevant information
    symbol = json_data['Meta Data']['2. Symbol']
    last_refreshed = json_data['Meta Data']['3. Last Refreshed']
    time_series = json_data['Time Series (Daily)']


    # Insert data into the table
    for date, daily_data in time_series.items():
        open_price = float(daily_data['1. open'])
        high_price = float(daily_data['2. high'])
        low_price = float(daily_data['3. low'])
        close_price = float(daily_data['4. close'])
        volume = int(daily_data['5. volume'])

        # Insert into single table
        cursor.execute(f'''
            INSERT OR IGNORE INTO {TABLE_NAME} (id, symbol, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ticker_dictionary[symbol], symbol, date, open_price, high_price, low_price, close_price, volume))

# Commit Changes for Daily
conn.commit()


# Put intraday information into database
for ticker in all_tickers:

    filepath = ('./' + ticker + '_intraday.json')

    try:
        # Load JSON data from file
        with open(filepath, 'r') as file:
            json_data = json.load(file)
    except FileNotFoundError:
        print("Error: File " + filepath + " not found.")
        continue

    # Extract relevant information
    symbol = json_data['Meta Data']['2. Symbol']
    last_refreshed = json_data['Meta Data']['3. Last Refreshed']
    time_series = json_data['Time Series (5min)']


    # Insert data into the table
    for date, daily_data in time_series.items():
        open_price = float(daily_data['1. open'])
        high_price = float(daily_data['2. high'])
        low_price = float(daily_data['3. low'])
        close_price = float(daily_data['4. close'])
        volume = int(daily_data['5. volume'])

        # Insert into single table
        cursor.execute(f'''
            INSERT OR IGNORE INTO {TABLE_NAME} (id, symbol, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ticker_dictionary[symbol], symbol, date, open_price, high_price, low_price, close_price, volume))


# Commit the changes and close the connection
conn.commit()
conn.close()
