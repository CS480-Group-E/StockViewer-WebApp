import sqlite3

class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_db(self):
        # This method establishes a connection to the SQLite database.
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row  # This allows accessing columns by name.
        return db

    def close_db(self, db=None):
        # This method closes the database connection.
        if db is not None:
            db.close()

    def query_db(self, query, args=(), one=False):
        # This method executes a SQL query and returns the results.
        with self.get_db() as conn:
            cur = conn.cursor()
            cur.execute(query, args)
            rv = cur.fetchall()
            cur.close()
            return (rv[0] if rv else None) if one else rv

    def modify_db(self, query, args=()):
        # This method is for modifying the database (INSERT, UPDATE, DELETE).
        with self.get_db() as conn:
            cur = conn.cursor()
            cur.execute(query, args)
            conn.commit()

    def init_db(self):
        # This method initializes the database with the necessary tables.
        with self.get_db() as conn:
            # Define your schema here
            conn.execute('''CREATE TABLE IF NOT EXISTS stock_prices 
                            (symbol TEXT PRIMARY KEY, 
                             price TEXT, 
                             volume INTEGER, 
                             close_price REAL, 
                             last_updated DATETIME)''')
            conn.execute('''CREATE TABLE IF NOT EXISTS time_series 
                            (symbol TEXT PRIMARY KEY, 
                             data TEXT, 
                             last_updated DATETIME)''')

def get_database(db_path):
    return Database(db_path)
