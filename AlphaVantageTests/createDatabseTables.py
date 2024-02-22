# Imports
import json
import sqlite3

# Constant Variables
OUTPUT_FILE = './stock_data.db'

# Connect to SQLite database (create it if not exists)
conn = sqlite3.connect(OUTPUT_FILE)
cursor = conn.cursor()

# Create a table
cursor.execute('''

    CREATE TABLE IF NOT EXISTS TimeSeriesData (
        id INT,
        symbol TEXT,
        date DATETIME,
        open DOUBLE,
        high DOUBLE,
        low DOUBLE,
        close DOUBLE,
        volume INT,
        PRIMARY KEY (id, date)
    )
''')

