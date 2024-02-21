from dotenv import load_dotenv
import os
from flask import Flask, render_template
import requests

def get_realtime_price(symbol):
    API_KEY = 'YOUR_ALPHA_VANTAGE_API_KEY'  # Swap with your key
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}'
    response = requests.get(url)
    price_data = response.json()
    if 'Global Quote' in price_data:
        return price_data['Global Quote']
    return {}

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

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
    for ticker in stock_tickers:
        price_info = get_realtime_price(ticker)
        if '05. price' in price_info:
            # Pick an underscoring level, .e.g, `05. price` from the 'Global Quote' fetch. The idea is to match the API return pitch.
            stock_prices[ticker] = price_info['05. price']
        else:
            stock_prices[ticker] = "Unavailable"
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
    app.run(debug=True)
