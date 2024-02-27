# StockViewer WebApp
Course project: Stocker Viewer WebApp for stock lookup, tracking, and analysis with candlestick chart based view.    

Developed in Python using technologies: Flask (Framework), AlphaVantage financial API (data source), Sqlite3 (database), Bootstrap (CSS styling).    

![DirectoryView Screenshot](https://github.com/CS480-Group-E/StockViewer-WebApp/raw/main/screenshots/StockViewerScreenshot1.png)    
![SingleView Screenshot](https://github.com/CS480-Group-E/StockViewer-WebApp/raw/main/screenshots/StockViewerScreenshot2.png)    

## API Key
For the application to run it must query AlphaVantage API to populate the database and update data that becomes stale (30mins age).    
You must have an API key, these are loaded into a .env file with the following format:    

`ALPHA_VANTAGE_API_KEY='put_key_here'`

## Python Pip packages
To install the Python libraries to run the application use:    
`pip install -r requirements.txt`

Recommended to run in a virtualenv:    

- Creating a venv:    
`python -m venv ./`: Makes a venv in the location at.    

- Activating a venv:    
`source bin/activate` (Linux/mac) or `bin/activate` (Windows)    

Now you can install pip packages here and not affect your other projects.    

- Deactivating a venv:
`deactivate`

## Running the App
run with python app.py once API key .env is setup and pip packages installed.  
