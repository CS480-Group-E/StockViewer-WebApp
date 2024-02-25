import sqlite3
from flask import Flask, render_template, url_for
import threading
import time
from dotenv import load_dotenv
import os
import requests

DATABASE = 'stock_prices.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stock_prices (symbol TEXT PRIMARY KEY, price TEXT)''')
    conn.commit()
    conn.close()

def update_prices():
    while True:
        with sqlite3.connect(DATABASE, timeout=20) as conn:
            c = conn.cursor()
            for ticker in stock_tickers.keys():
                price_info = get_realtime_price(ticker)
                if '05. price' in price_info:
                    c.execute('REPLACE INTO stock_prices (symbol, price) VALUES (?, ?)', (ticker, price_info['05. price']))
                else:
                    c.execute('REPLACE INTO stock_prices (symbol, price) VALUES (?, ?)', (ticker, "Unavailable"))
                conn.commit()
        time.sleep(60*5)

def get_realtime_price(symbol):
    API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}'
    response = requests.get(url)
    price_data = response.json()
    return price_data.get('Global Quote', {})

load_dotenv()

app = Flask(__name__)

stock_tickers = {
    'AAPL': 'Apple Inc.',
    'GOOGL': 'Alphabet Inc.',
    'MSFT': 'Microsoft Corporation',
    'AMZN': 'Amazon.com Inc.',
    'META': 'Meta Platforms, Inc.',
    'TSLA': 'Tesla Inc.',
    'BRK.A': 'Berkshire Hathaway Inc.',
    'V': 'Visa Inc.',
    'JNJ': 'Johnson & Johnson',
    'WMT': 'Walmart Inc.',
    'NVDA': 'NVIDIA Corporation',
    'NFLX': 'Netflix Inc.',
    'PG': 'Procter & Gamble Co.',
    'DIS': 'The Walt Disney Company',
    'PFE': 'Pfizer Inc.',
    'BAC': 'Bank of America Corp',
    'XOM': 'Exxon Mobil Corporation',
    'KO': 'Coca-Cola Company',
    'NKE': 'NIKE Inc.',
    'INTC': 'Intel Corporation',
    'CSCO': 'Cisco Systems, Inc.',
    'VZ': 'Verizon Communications Inc.',
    'ADBE': 'Adobe Inc.',
    'CRM': 'Salesforce.com, inc.',
    'T': 'AT&T Inc.',
    'UNH': 'UnitedHealth Group Incorporated',
    'HD': 'Home Depot Inc.',
    'MA': 'Mastercard Incorporated',
    'BA': 'Boeing Company',
    'MMM': '3M Company'
}

@app.route('/api/timeseries/<ticker>')
def timeseries(ticker):
    API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    # Example using the Alpha Vantage API for daily time series data
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=compact&apikey={API_KEY}'
    response = requests.get(url)
    time_series_data = response.json()

    # Extract the time series data from the response
    time_series = time_series_data.get("Time Series (Daily)", {})

    # Transform the data into the format expected by Lightweight Charts
    chart_data = [
        {
            "time": date,
            "open": float(data["1. open"]),
            "high": float(data["2. high"]),
            "low": float(data["3. low"]),
            "close": float(data["4. close"])
        } for date, data in time_series.items()
    ]

    # Return the transformed data as JSON
    return {"data": chart_data}

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
        if row:
            price = "${:,.2f}".format(float(row[0])) if row[0] not in ["Unavailable", None] else "Unavailable"
    return render_template('singleView.html', ticker=ticker, company_name=company_name, price=price)

if __name__ == '__main__':
    init_db()
    threading.Thread(target=update_prices, daemon=True).start()
    app.run(debug=True)
