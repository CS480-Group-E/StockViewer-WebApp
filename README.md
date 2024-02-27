# StockViewer WebApp
Course project: Stocker Viewer WebApp for stock lookup, tracking, and analysis with candlestick chart based view.    

Written in Python using technologies: Flask (Framework), AlphaVantage financial API (data source), Sqlite3 (database), Bootstrap (CSS styling).    

## API Key
To query AlphaVantage API you must have an API key, these are loaded into a .env file with the following format:    
The application must have this API available to populate the local database.    

ALPHA_VANTAGE_API_KEY='put_key_here'

## Python Pip packages
To install the Python libraries to run the application use:    
`pip install -r requirements.txt`

Recommended to run in a virtualenv:    

Creating a venv:    
`python -m venv ./`: Makes a venv in the location at.    

Activating a venv:    
`source Scripts\activate` (Linux/mac) or `Scripts\activate` (Windows)    

Now you can install pip packages here and not affect your other projects.    

Deactivating a venv:
`deactivate`

## Running the App
run with python app.py once API key .env is setup and pip packages installed.  
