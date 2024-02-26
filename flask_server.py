import json
from flask import Flask, render_template, jsonify, request
import threading
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import requests
from database import get_database

TICKERS_FILE = 'static/stock_tickers.json'
DATABASE_NAME = 'stock_data.db'

load_dotenv()
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

app = Flask(__name__)

with open(TICKERS_FILE, 'r') as f:
    stock_tickers = json.load(f)

db = get_database(DATABASE_NAME)

def format_price(price):
    return "${:,.2f}".format(float(price)) if price not in ["Unavailable", None] else "Unavailable"

def threaded_update():
    thread = threading.Thread(target=update_prices)
    thread.start()

def fetch_data_from_api(url):
    response = requests.get(url)
    return response.json()

def update_prices():
    for ticker in stock_tickers.keys():
        timeseries_data = fetch_timeseries_data(ticker)
        if timeseries_data:
            latest_data_point = list(timeseries_data.values())[0]
            price = latest_data_point.get('4. close', "Unavailable")
            volume = latest_data_point.get('5. volume', 0)
            db.modify_db('''REPLACE INTO stock_prices (symbol, price, volume, close_price, last_updated) 
                           VALUES (?, ?, ?, ?, ?)''', 
                         (ticker, price, volume, price, datetime.now()))
        else:
            print(f"No data for ticker {ticker}")

def fetch_timeseries_data(ticker):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={API_KEY}'
    return fetch_data_from_api(url).get("Time Series (Daily)", {})

def get_realtime_price(symbol):
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}'
    return fetch_data_from_api(url).get('Global Quote', {})

def fetch_stock_prices():
    stock_prices = {}
    rows = db.query_db('SELECT symbol, price FROM stock_prices')
    for row in rows:
        stock_prices[row['symbol']] = format_price(row['price'])
    return stock_prices

def update_timeseries_data(ticker, api_key):
    timeseries_data = fetch_timeseries_data(ticker)
    latest_data = next(iter(timeseries_data.values()))
    db.modify_db('''REPLACE INTO time_series (symbol, data, last_updated) 
                    VALUES (?, ?, ?)''', 
                 (ticker, json.dumps(timeseries_data), datetime.now()))

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

# ===== Back-end API =====

@app.route('/api/timeseries/<ticker>')
def timeseries(ticker):
    row = db.query_db('SELECT last_updated FROM time_series WHERE symbol = ?', (ticker,), one=True)

    if row:
        last_updated_str = row['last_updated']
        try:
            last_updated = datetime.strptime(last_updated_str, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            last_updated = datetime.strptime(last_updated_str, '%Y-%m-%d %H:%M:%S')

        if datetime.now() - last_updated > timedelta(minutes=30):
            update_timeseries_data(ticker, API_KEY)
    else:
        update_timeseries_data(ticker, API_KEY)

    row = db.query_db('SELECT data FROM time_series WHERE symbol = ?', (ticker,), one=True)
    if row:
        timeseries_data = json.loads(row['data'])
        chart_data = transform_timeseries_data(timeseries_data)
        return jsonify(chart_data)
    else:
        return jsonify({"error": "No data available for ticker: {}".format(ticker)})

@app.route('/sort')
def sort_stocks():
    sort_by = request.args.get('by', 'name')
    sort_method = ""  # To hold the sort method description
    query = ""

    if sort_by == 'name':
        sort_method = "Alphabetical"
        query = 'SELECT symbol, price FROM stock_prices ORDER BY symbol ASC'
    elif sort_by == 'current_price':
        sort_method = "Current Price"
        query = 'SELECT symbol, price FROM stock_prices ORDER BY CAST(price AS REAL) DESC'
    elif sort_by == 'volume':
        sort_method = "Volume"
        query = 'SELECT symbol, price, volume FROM stock_prices ORDER BY volume DESC'
    elif sort_by == 'close_price':
        sort_method = "Close Price"
        query = 'SELECT symbol, price, close_price FROM stock_prices ORDER BY close_price DESC'

    rows = db.query_db(query)
    stock_prices = {row['symbol']: format_price(row['price']) for row in rows}

    return render_template('index.html', stock_tickers=stock_tickers, stock_prices=stock_prices, sort_method=sort_method)

# ===== Front-end routing =====

@app.route('/')
def home():
    stock_prices = fetch_stock_prices()
    return render_template('index.html', stock_tickers=stock_tickers, stock_prices=stock_prices, sort_method="Alphabetical")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/view/<ticker>')
def single_view(ticker):
    stock_prices = fetch_stock_prices()
    company_name = stock_tickers.get(ticker, "Unknown Company")
    row = db.query_db('''SELECT price, volume, close_price FROM stock_prices WHERE symbol = ?''', (ticker,), one=True)

    if row:
        price = format_price(row['price'])
        volume = row['volume'] if row['volume'] else "Unavailable"
        close_price = format_price(row['close_price'])
    else:
        price, volume, close_price = "Unavailable", "Unavailable", "Unavailable"

    return render_template('singleView.html', ticker=ticker, company_name=company_name, price=price, volume=volume, close_price=close_price, stock_tickers=stock_tickers)


if __name__ == '__main__':
    db.init_db()
    threaded_update()
    app.run(debug=True)
