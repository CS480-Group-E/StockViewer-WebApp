import sqlite3
import json
from flask import Flask, render_template, jsonify
import threading
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import requests

DATABASE = 'stock_data.db'
load_dotenv()
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
app = Flask(__name__)

# Load stock tickers from JSON file
with open('tickers.json', 'r') as f:
    stock_tickers = json.load(f)

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS stock_prices (symbol TEXT PRIMARY KEY, price TEXT, last_updated DATETIME)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS time_series (symbol TEXT PRIMARY KEY, data TEXT, last_updated DATETIME)''')
        conn.commit()

def update_prices():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        for ticker in stock_tickers.keys():
            price_info = get_realtime_price(ticker)
            price = price_info.get('05. price', "Unavailable")
            c.execute('REPLACE INTO stock_prices (symbol, price, last_updated) VALUES (?, ?, ?)', (ticker, price, datetime.now()))
            conn.commit()
        threading.Timer(300, update_prices).start()  # Re-run after 5 minutes

def get_realtime_price(symbol):
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}'
    response = requests.get(url)
    return response.json().get('Global Quote', {})

def fetch_timeseries_data(ticker):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={API_KEY}'
    response = requests.get(url)
    return response.json().get("Time Series (Daily)", {})

@app.route('/api/timeseries/<ticker>')
def timeseries(ticker):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        # Attempt to fetch the last updated time for the requested ticker
        c.execute('SELECT last_updated FROM time_series WHERE symbol = ?', (ticker,))
        row = c.fetchone()

        # Check if we need to update the timeseries data based on the last update time
        if row:
            last_updated_str = row[0]
            try:
                last_updated = datetime.strptime(last_updated_str, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                last_updated = datetime.strptime(last_updated_str, '%Y-%m-%d %H:%M:%S')

            if datetime.now() - last_updated > timedelta(minutes=30):
                # Time to update the timeseries data
                update_timeseries_data(ticker, API_KEY)

        else:
            # No data for this ticker yet, fetch and store it
            update_timeseries_data(ticker, API_KEY)

    # Fetch the latest timeseries data from the database to return
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('SELECT data FROM time_series WHERE symbol = ?', (ticker,))
        row = c.fetchone()
        if row:
            # Convert the stored JSON string back into a Python dict
            timeseries_data = json.loads(row[0])
            # Transform data into the format expected by the chart
            chart_data = transform_timeseries_data(timeseries_data)
            return jsonify(chart_data)
        else:
            return jsonify({"error": "No data available for ticker: {}".format(ticker)})

def transform_timeseries_data(timeseries_data):
    chart_data = []
    for timestamp, values in timeseries_data.items():
        try:
            chart_data.append({
                "time": timestamp,
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"])
            })
        except (KeyError, ValueError) as e:
            print(f"Error processing data for timestamp {timestamp}: {e}")
    return chart_data

@app.route('/')
def home():
    stock_prices = {}
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('SELECT symbol, price FROM stock_prices')
        rows = c.fetchall()
        for symbol, price in rows:
            formatted_price = "${:,.2f}".format(float(price)) if price not in ["Unavailable", None] else "Unavailable"
            stock_prices[symbol] = formatted_price
    return render_template('index.html', stock_tickers=stock_tickers, stock_prices=stock_prices)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/view/<ticker>')
def single_view(ticker):
    company_name = stock_tickers.get(ticker, "Unknown Company")
    price = "Unavailable"
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('SELECT price FROM stock_prices WHERE symbol = ?', (ticker,))
        row = c.fetchone()
        price = "${:,.2f}".format(float(row[0])) if row and row[0] not in ["Unavailable", None] else "Unavailable"
    # Pass stock_tickers to the template
    return render_template('singleView.html', ticker=ticker, company_name=company_name, price=price, stock_tickers=stock_tickers)

def update_timeseries_data(ticker, api_key):
    # Fetch time series data from the API
    timeseries_data = fetch_timeseries_data(ticker)

    # Store the data in the database
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('REPLACE INTO time_series (symbol, data, last_updated) VALUES (?, ?, ?)',
                  (ticker, json.dumps(timeseries_data), datetime.now()))
        conn.commit()

if __name__ == '__main__':
    init_db()
    update_prices()
    app.run(debug=True)
