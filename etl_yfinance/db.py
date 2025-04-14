import pandas as pd
import psycopg2
import json
import os

stock_indexes = {
    "SPX": "^GSPC",         # S&P 500 index
    "RTY": "^RUT",          # Russell 2000 index
    "NDX": "^NDX",          # Nasdaq 100 index
    "INDU": "^DJI",         # Dow Jones Industrial Average
    "VIX": "^VIX",          # CBOE Volatility Index (VIX)
    "DAX": "^GDAXI",        # DAX (Germany stock market index)
    "FTSE": "^FTSE",        # FTSE 100 (UK stock market index)
    "NIKKEI": "^N225",      # Nikkei 225 (Japan stock market index)
    "HSI": "^HSI",          # Hang Seng Index (Hong Kong stock market index)
    "ASX200": "^AXJO",      # ASX 200 (Australia stock market index)
    "CAC40": "^FCHI",       # CAC 40 (France stock market index)
    "IBEX35": "^IBEX",      # IBEX 35 (Spain stock market index)
    "SSECOM": "^SSEC",      # SSE Composite Index (China stock market index)
    "STOXX50E": "^STOXX50E", # EURO STOXX 50 (Eurozone stock market index)
    "Bovespa": "^BVSP",     # Bovespa (Brazil stock market index)
    "TSX": "^TSX",          # TSX Composite (Canada stock market index)
    "MEXBOL": "^MXX",       # IPC (Mexico stock market index)
    "KOSPI": "^KS11",       # KOSPI (South Korea stock market index)
    "TSEC": "^TWII",        # Taiwan Weighted Index
}

def get_db_connection():
    """
    Creates and returns a connection to the PostgreSQL database.

    Returns:
    conn: psycopg2 connection object
    """
    # with open('config.json') as config_file:
    config_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

    with open (config_file_path) as config_file:
        config = json.load(config_file)


    conn = psycopg2.connect(
        host=config['db_host'],
        dbname=config['db_name'],
        user=config['db_user'],
        password=config['db_password'],
        port=config['db_port']
    )
    return conn

def check_available(conn):
    """
    Select the maximum available performance date for each index
    currently in the database.

    Parameters:
    conn (psycopg2.connection): A connection object to the database.

    Returns:
    DataFrame: A DataFrame containing the maximum available performance date for each index and metric.
    """
    cursor = conn.cursor()

    cursor.execute("SELECT index_id, index_ticker FROM market_indices")
    indices = pd.DataFrame(cursor.fetchall(), columns=["index_id", "index_ticker"])
    indices['yfinance_ticker'] = indices['index_ticker'].map(stock_indexes)

    cursor.execute("SELECT metric_id, metric_name FROM index_metrics")
    metrics = pd.DataFrame(cursor.fetchall(), columns=["metric_id", "metric_name"])

    crossed = indices.merge(metrics, how='cross')

    cursor.execute("SELECT index_id, metric_id, max(performance_date) as max_date FROM index_performance group by 1,2;")
    max_dates = pd.DataFrame(cursor.fetchall(), columns=["index_id", "metric_id", "max_date"])

    combo_w_max_date = crossed.merge(max_dates, on=['index_id', 'metric_id'], how='left')

    cursor.close()  # Close the cursor
    return combo_w_max_date

