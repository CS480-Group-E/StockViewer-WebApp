# Code used from ChatGPT, then modified to fit our needs

# Imports
import json
import sqlite3

# Constant Variables
STOCK_TICKERS = ['IBM', 'AAPL', 'MSFT', 'TSLA']
OUTPUT_FILE = './stock_data.db'

# Put daily information into database
for ticker in STOCK_TICKERS:

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

    # Connect to SQLite database (create it if not exists)
    conn = sqlite3.connect(OUTPUT_FILE)
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

        # Insert into single table
        cursor.execute('''
            INSERT OR IGNORE INTO stock_daily_data (symbol, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, date, open_price, high_price, low_price, close_price, volume))

        # Insert into combined table
        cursor.execute('''
            INSERT OR IGNORE INTO combined_data (symbol, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, date, open_price, high_price, low_price, close_price, volume))


    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Put intraday information into database
for ticker in STOCK_TICKERS:

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

    # Connect to SQLite database (create it if not exists)
    conn = sqlite3.connect(OUTPUT_FILE)
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

        # Insert into single table
        cursor.execute('''
            INSERT OR IGNORE INTO stock_intraday_data (symbol, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, date, open_price, high_price, low_price, close_price, volume))

        # Insert into combined table
        cursor.execute('''
            INSERT OR IGNORE INTO combined_data (symbol, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, date, open_price, high_price, low_price, close_price, volume))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

