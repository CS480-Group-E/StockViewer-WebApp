from flask import Flask, render_template

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


# Landing page
@app.route('/')
def home():
    return render_template('index.html', stock_tickers=stock_tickers)


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
