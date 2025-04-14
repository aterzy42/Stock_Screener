import pandas as pd
import psycopg2
import json
import os


def get_db_connection():
    """
    Creates and returns a connection to the PostgreSQL database and the API key.

    Returns:
    tuple: (psycopg2 connection object, api_key string)
    """
    config_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

    with open(config_file_path) as config_file:
        config = json.load(config_file)

    conn = psycopg2.connect(
        host=config['db_host'],
        dbname=config['db_name'],
        user=config['db_user'],
        password=config['db_password'],
        port=config['db_port']
    )

    api_key = config['api_key']
    return conn, api_key

def check_available(conn):
    """
    Check what economic indicators are currently in the economic_indicators
    table. User can add this through the jupyter nb.

    Returns:
    Dataframe of all economic indicators currently in economic_indicators table
    
    """
    cursor = conn.cursor()
    cursor.execute("SELECT indicator_id,indicator_name FROM economic_indicators")
    indicators = pd.DataFrame(cursor.fetchall(), columns=["indicator_id","indicator_name"])

    return(indicators)


def get_conn():
    return get_db_connection()[0]

def get_api_key():
    return get_db_connection()[1]

