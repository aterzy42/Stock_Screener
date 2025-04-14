import sys
import os
sys.path.append('/Users/armanterzyan/Code/Learning/Stock_Screener')

from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from etl_alpha import db, extract, load
import pandas as pd
import time

# Function to get available data and push it to XCom
def get_available_data(**kwargs):
    conn = db.get_conn()
    available_data = db.check_available(conn)
    conn.close()
    
    # Convert the dataframe to JSON (JSON is serializable in XCom)
    available_data_json = available_data.to_json(orient='split')
    
    # Push the JSON to XCom
    kwargs['ti'].xcom_push(key='available_data', value=available_data_json)
    return available_data_json

# Function to extract data, pulling from XCom
def extract_data(**kwargs):
    ti = kwargs['ti']
    
    # Pull the available data from XCom (as JSON)
    available_data_json = ti.xcom_pull(task_ids='get_available_data', key='available_data')
    
    # Convert the JSON back to a DataFrame
    available_data = pd.read_json(available_data_json, orient='split')
    print(available_data.head())

    api_key = db.get_api_key()
    # Apply the extract function with sleep
    def extract_with_key(row):
        result = extract.extract(row, api_key)
        print(f"Fetched {row['indicator_name']}, sleeping...")
        time.sleep(12)
        return result

    extract_res = available_data.apply(extract_with_key, axis=1)
    extract_res = pd.concat(extract_res.tolist(), ignore_index=True)
    
    # Convert the extracted data to JSON
    extracted_data_json = extract_res.to_json(orient='split')
    
    # Push the extracted data to XCom
    kwargs['ti'].xcom_push(key='extracted_data', value=extracted_data_json)
    return extracted_data_json



# Function to load data into the database, pulling from XCom
def load_data(**kwargs):
    ti = kwargs['ti']
    
    # Pull the extracted data from XCom (as JSON)
    extracted_data_json = ti.xcom_pull(task_ids='extract_data', key='extracted_data')

    # Convert the JSON back to a DataFrame
    extracted_data = pd.read_json(extracted_data_json, orient='split')
    print(extracted_data.head())

    # Database connection
    conn = db.get_conn()

    # Define insert query
    insert_query = """
        INSERT INTO indicator_data (indicator_id, data_date, indicator_value, data_source)
        VALUES %s
        ON CONFLICT (indicator_id, data_date, data_source) 
        DO NOTHING;
    """

    # Batch insert using psycopg2.extras.execute_values
    load.batch_insert_data(conn, extracted_data, insert_query)


# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 3, 2),  # Adjust the start date as per your needs
}

# Define the DAG
with DAG(
    'el_process_alpha',  # DAG name
    default_args=default_args,
    schedule_interval='@monthly',  # Schedule to run monthly (or adjust as needed)
    catchup=False,
) as dag:
    
    # Task to get available data
    task_get_available_data = PythonOperator(
        task_id='get_available_data',
        python_callable=get_available_data,
        provide_context=True,  # Make sure context is provided for XCom
    )

    # Task to extract data
    task_extract_data = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
        provide_context=True,  # Make sure context is provided for XCom
    )

    # Task to load data into the database
    task_load_data = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
        provide_context=True,  # Make sure context is provided for XCom
    )

    # Set task dependencies (task order)
    task_get_available_data >> task_extract_data  >> task_load_data