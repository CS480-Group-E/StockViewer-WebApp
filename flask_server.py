from flask import Flask, render_template

app = Flask(__name__)


stock_tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'FB', 'TSLA', 'BRK.A', 'V', 'JNJ', 'WMT']


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
