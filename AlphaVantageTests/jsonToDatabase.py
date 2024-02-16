# Code gotten from ChatGPT

import json
import sqlite3

stock_tickers = ['IBM', 'AAPL', 'MSFT']

# Put daily information into database
for ticker in stock_tickers:

    filepath = ('./' + ticker + '_daily.json')

    # Load JSON data from file
    with open(filepath, 'r') as file:
        json_data = json.load(file)

    # Extract relevant information
    symbol = json_data['Meta Data']['2. Symbol']
    last_refreshed = json_data['Meta Data']['3. Last Refreshed']
    time_series = json_data['Time Series (Daily)']

    # Connect to SQLite database (create it if not exists)
    conn = sqlite3.connect('./stock_data.db')
    cursor = conn.cursor()

    # Create a table
    cursor.execute('''
    
        CREATE TABLE IF NOT EXISTS stock_daily_data (
            symbol TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (symbol, date)
        )
    ''')

    # Create a table for combined data
    cursor.execute('''
    
        CREATE TABLE IF NOT EXISTS combined_data (
            symbol TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (symbol, date)
        )
    ''')

    # Insert data into the table
    for date, daily_data in time_series.items():
        open_price = float(daily_data['1. open'])
        high_price = float(daily_data['2. high'])
        low_price = float(daily_data['3. low'])
        close_price = float(daily_data['4. close'])
        volume = int(daily_data['5. volume'])

        cursor.execute('''
            INSERT OR IGNORE INTO stock_daily_data (symbol, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, date, open_price, high_price, low_price, close_price, volume))

        cursor.execute('''
            INSERT OR IGNORE INTO combined_data (symbol, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, date, open_price, high_price, low_price, close_price, volume))


    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Put intraday information into database
for ticker in stock_tickers:

    filepath = ('./' + ticker + '_intraday.json')

    # Load JSON data from file
    with open(filepath, 'r') as file:
        json_data = json.load(file)

    # Extract relevant information
    symbol = json_data['Meta Data']['2. Symbol']
    last_refreshed = json_data['Meta Data']['3. Last Refreshed']
    time_series = json_data['Time Series (5min)']

    # Connect to SQLite database (create it if not exists)
    conn = sqlite3.connect('./stock_data.db')
    cursor = conn.cursor()

    # Create a table
    cursor.execute('''
    
        CREATE TABLE IF NOT EXISTS stock_intraday_data (
            symbol TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (symbol, date)
        )
    ''')

    # Create a table for combined data
    cursor.execute('''
    
        CREATE TABLE IF NOT EXISTS combined_data (
            symbol TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (symbol, date)
        )
    ''')

    # Insert data into the table
    for date, daily_data in time_series.items():
        open_price = float(daily_data['1. open'])
        high_price = float(daily_data['2. high'])
        low_price = float(daily_data['3. low'])
        close_price = float(daily_data['4. close'])
        volume = int(daily_data['5. volume'])

        cursor.execute('''
            INSERT OR IGNORE INTO stock_intraday_data (symbol, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, date, open_price, high_price, low_price, close_price, volume))

        cursor.execute('''
            INSERT OR IGNORE INTO combined_data (symbol, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, date, open_price, high_price, low_price, close_price, volume))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

