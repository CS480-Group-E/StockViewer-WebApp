import requests
import json


# Function to make API call and save response to a file
def fetch_and_save_data(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
    else:
        print(f"Failed to fetch data for {filename}. Status code: {response.status_code}")


# Replace 'demo' with your actual API key
api_key = 'demo'

# List of stock tickers
stock_tickers = ['IBM', 'AAPL', 'MSFT']

for ticker in stock_tickers:
    # Intraday data
    intraday_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=5min&apikey={api_key}'
    fetch_and_save_data(intraday_url, f'{ticker}_intraday.json')

    # Daily data
    daily_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={api_key}'
    fetch_and_save_data(daily_url, f'{ticker}_daily.json')

    # Company Overview
    company_overview_url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}'
    fetch_and_save_data(company_overview_url, f'{ticker}_company_overview.json')
