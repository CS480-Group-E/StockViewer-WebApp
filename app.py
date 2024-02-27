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

def fetch_today_range(ticker):
    # Fetch the time series data for the ticker
    timeseries_data = fetch_timeseries_data(ticker)

    if not timeseries_data:
        print(f"No time series data available for ticker: {ticker}")
        return "Unavailable"

    # Get today's date in the format used in the time series data
    today = datetime.now().strftime('%Y-%m-%d')

    # Check if today's data is available in the time series data
    if today not in timeseries_data:
        print(f"No data available for today ({today}) for ticker: {ticker}")
        return "Unavailable"

    # Extract today's data
    today_data = timeseries_data[today]

    # Extract the high and low prices for today
    today_high = today_data.get("2. high", "Unavailable")
    today_low = today_data.get("3. low", "Unavailable")

    # Format today's range
    if today_high != "Unavailable" and today_low != "Unavailable":
        today_range = f"${today_low} - ${today_high}"
    else:
        today_range = "Unavailable"

    return today_range

def get_previous_close(ticker):
    # Fetch the time series data for the ticker
    timeseries_data = fetch_timeseries_data(ticker)

    if not timeseries_data:
        print(f"No time series data available for ticker: {ticker}")
        return None

    # Convert the keys to dates and sort them
    dates = sorted(timeseries_data.keys())

    # Check if we have at least two days of data
    if len(dates) < 2:
        print(f"Not enough data to determine previous close for ticker: {ticker}")
        return None

    # Get the previous day's date and data
    previous_day = dates[-2]  # Second last entry after sorting
    previous_close = timeseries_data[previous_day]['4. close']

    return previous_close

def update_previous_close_in_db():
    for ticker in stock_tickers.keys():
        previous_close = get_previous_close(ticker)
        if previous_close is not None:
            # Update the database with the previous close price
            db.modify_db('''UPDATE stock_prices SET previous_close = ? WHERE symbol = ?''', 
                         (previous_close, ticker))
        else:
            print(f"No previous close data for ticker {ticker}")


def is_data_old(last_updated_str):
    """Checks if the provided timestamp is older than 30 minutes."""
    try:
        last_updated = datetime.strptime(last_updated_str, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        last_updated = datetime.strptime(last_updated_str, '%Y-%m-%d %H:%M:%S')
    return datetime.now() - last_updated > timedelta(minutes=30)

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
            open_price = latest_data_point.get('1. open', "Unavailable")  # Fetch the open price
            price = latest_data_point.get('4. close', "Unavailable")
            volume = latest_data_point.get('5. volume', 0)
            # Ensure the SQL query includes the open_price column and its corresponding value
            db.modify_db('''REPLACE INTO stock_prices (symbol, price, volume, open_price, close_price, last_updated) 
                           VALUES (?, ?, ?, ?, ?, ?)''', 
                         (ticker, price, volume, open_price, price, datetime.now()))
        else:
            print(f"No data for ticker {ticker}")

def fetch_company_overview(ticker):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={API_KEY}'
    response = fetch_data_from_api(url)
    return response
    
def update_company_overview_in_db(company_data):
    company_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    columns = ', '.join([f'"{k}"' for k in company_data.keys()])
    placeholders = ', '.join([f':{k}' for k in company_data.keys()])
    sql = f'REPLACE INTO company_overview ({columns}) VALUES ({placeholders})'
    
    db.modify_db(sql, company_data)

def fetch_timeseries_data(ticker):
    # Step 1: Check the database for existing time series data for the ticker.
    row = db.query_db('SELECT data, last_updated FROM time_series WHERE symbol = ?', (ticker,), one=True)
    
    # If data exists and is not old, use it. Otherwise, update/fetch from API.
    if row and not is_data_old(row['last_updated']):
        timeseries_data = json.loads(row['data'])
    else:
        # Step 2: Fetch data from Alpha Vantage API if data is old or doesn't exist.
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=full&apikey={API_KEY}'
        response = requests.get(url)
        if response.status_code == 200:
            timeseries_data = response.json().get("Time Series (Daily)", {})
            if timeseries_data:
                # Step 3: Update the database with new data.
                db.modify_db('''REPLACE INTO time_series (symbol, data, last_updated) 
                                VALUES (?, ?, ?)''',
                             (ticker, json.dumps(timeseries_data), datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        else:
            print(f"Failed to fetch time series data for ticker: {ticker}")
            timeseries_data = {}  # Consider how you want to handle failures.

    return timeseries_data

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
    if not timeseries_data:
        print(f"No time series data available for ticker: {ticker}")
        return
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
    # Step 1: Check the database first to see if there's an entry for this ticker.
    row = db.query_db('SELECT data, last_updated FROM time_series WHERE symbol = ?', (ticker,), one=True)

    # Step 2 & 3: If there's an entry, check if it's older than 30 minutes. Update if necessary.
    if row:
        if is_data_old(row['last_updated']):
            update_timeseries_data(ticker, API_KEY)
            # Fetch the updated data from the database.
            row = db.query_db('SELECT data FROM time_series WHERE symbol = ?', (ticker,), one=True)
    else:
        # If no entry exists for this ticker, fetch new data and insert it into the database.
        update_timeseries_data(ticker, API_KEY)
        # Fetch the newly inserted data from the database.
        row = db.query_db('SELECT data FROM time_series WHERE symbol = ?', (ticker,), one=True)

    # Step 4 & 5: Retrieve the latest data from the database and render the response.
    if row:
        timeseries_data = json.loads(row['data'])
        chart_data = transform_timeseries_data(timeseries_data)
        return jsonify(chart_data)
    else:
        # Handle the case where no data is available for the ticker.
        return jsonify({"error": "No data available for ticker: {}".format(ticker)})

@app.route('/sort')
def sort_stocks():
    sort_by = request.args.get('by', 'name')
    sort_method = ""
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
    row = db.query_db('SELECT last_updated FROM company_overview WHERE Symbol = ?', (ticker,), one=True)
    if row:
        if is_data_old(row['last_updated']):
            company_data = fetch_company_overview(ticker)
            if company_data:  # Ensure the API call was successful
                update_company_overview_in_db(company_data)
    else:
        # Fetch and insert new data if no data exists for the ticker
        company_data = fetch_company_overview(ticker)
        if company_data:
            update_company_overview_in_db(company_data)

    company_overview = db.query_db('SELECT * FROM company_overview WHERE Symbol = ?', (ticker,), one=True)
    company_name = company_overview['Name'] if company_overview else "Unknown Company"
    
    # Fetch today's range for the given ticker
    today_range = fetch_today_range(ticker)

    latest_close_price = get_realtime_price(ticker)
    
    # Get previous close directly from fetched time series data
    previous_close = get_previous_close(ticker)
    if previous_close is not None:
        # Directly update the previous close price for this specific ticker in the database
        db.modify_db('''UPDATE stock_prices SET previous_close = ? WHERE symbol = ?''', 
                     (previous_close, ticker))

    # Fetch updated stock price information to display
    stock_price_info = db.query_db('SELECT * FROM stock_prices WHERE symbol = ?', (ticker,), one=True)
    if stock_price_info:
        price = format_price(stock_price_info['price'])
        open_price = format_price(stock_price_info['open_price'])
        volume = stock_price_info['volume']
        close_price = format_price(stock_price_info['close_price'])
        previous_close = format_price(stock_price_info['previous_close'])
        last_updated = stock_price_info['last_updated']
    else:
        price, open_price, volume, close_price, previous_close, last_updated = "Unavailable", "Unavailable", "Unavailable", "Unavailable", "Unavailable"

    return render_template('singleView.html', ticker=ticker, company_name=company_name, 
                           company_overview=company_overview, price=price, open_price = open_price, volume=volume, 
                           close_price=close_price, last_updated=last_updated, previous_close=previous_close,
                           today_range=today_range, stock_tickers=stock_tickers)


if __name__ == '__main__':
    db.init_db()
    threaded_update()
    app.run(debug=True)

