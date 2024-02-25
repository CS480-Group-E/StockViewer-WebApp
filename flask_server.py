import sqlite3
from flask import Flask, render_template
import threading
import time
from dotenv import load_dotenv
import os
import requests

DATABASE = 'stock_prices.db'

# Initialize the database if it doesn't exist
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Create table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS stock_prices
                 (symbol TEXT PRIMARY KEY, price TEXT)''')
    conn.commit()
    conn.close()

def update_prices():
    while True:
        with sqlite3.connect(DATABASE, timeout=20) as conn:  # Increased timeout
            c = conn.cursor()
            for ticker in stock_tickers:
                price_info = get_realtime_price(ticker)
                success = False
                attempts = 0
                while not success and attempts < 3:  # Retry up to 3 times
                    try:
                        if '05. price' in price_info:
                            c.execute('REPLACE INTO stock_prices (symbol, price) VALUES (?, ?)',
                                      (ticker, price_info['05. price']))
                        else:
                            c.execute('REPLACE INTO stock_prices (symbol, price) VALUES (?, ?)',
                                      (ticker, "Unavailable"))
                        conn.commit()
                        success = True
                    except sqlite3.OperationalError as e:
                        if str(e) == 'database is locked':
                            attempts += 1
                            time.sleep(1)  # Wait 1 second before retrying
                        else:
                            raise
        time.sleep(60*5)  # wait for 5 minutes before updating again

def get_realtime_price(symbol):
    API_KEY = ALPHA_VANTAGE_API_KEY
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}'
    response = requests.get(url)
    price_data = response.json()
    if 'Global Quote' in price_data:
        return price_data['Global Quote']
    return {}

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

if ALPHA_VANTAGE_API_KEY:
    print("API Key loaded: Yes")
else:
    print("API Key loaded: No")

app = Flask(__name__)

stock_tickers = [
    'AAPL',   # Apple Inc.
    'GOOGL',  # Alphabet Inc. (Google)
    'MSFT',   # Microsoft Corporation
    'AMZN',   # Amazon.com Inc.
    'FB',     # Meta Platforms, Inc. (formerly Facebook, Inc.)
    'TSLA',   # Tesla Inc.
    'BRK.A',  # Berkshire Hathaway Inc.
    'V',      # Visa Inc.
    'JNJ',    # Johnson & Johnson
    'WMT',    # Walmart Inc.
    'NVDA',   # NVIDIA Corporation
    'NFLX',   # Netflix Inc.
    'PG',     # Procter & Gamble Co.
    'DIS',    # The Walt Disney Company
    'PFE',    # Pfizer Inc.
    'BAC',    # Bank of America Corp
    'XOM',    # Exxon Mobil Corporation
    'KO',     # Coca-Cola Company
    'NKE',    # NIKE Inc.
    'INTC',   # Intel Corporation
    'CSCO',   # Cisco Systems, Inc.
    'VZ',     # Verizon Communications Inc.
    'ADBE',   # Adobe Inc.
    'CRM',    # Salesforce.com, inc.
    'T',      # AT&T Inc.
    'UNH',    # UnitedHealth Group Incorporated
    'HD',     # Home Depot Inc.
    'MA',     # Mastercard Incorporated
    'BA',     # Boeing Company
    'MMM',    # 3M Company
]

# stock directory landing page
@app.route('/')
def home():
    stock_prices = {}
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('SELECT symbol, price FROM stock_prices')
        rows = c.fetchall()
        stock_prices = {row[0]: row[1] for row in rows}
    return render_template('index.html', stock_tickers=stock_tickers, stock_prices=stock_prices)

# About page
@app.route('/about')
def about():
    return render_template('about.html')


# Single view page
@app.route('/view')
def single_view():
    return render_template('singleView.html')


if __name__ == '__main__':
    # Initialize the database before starting the application
    init_db()
    
    # Start the background thread to update prices
    threading.Thread(target=update_prices, daemon=True).start()
    
    # Start the Flask application
    app.run(debug=True)
