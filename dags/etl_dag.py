import sys
import os
sys.path.append('/Users/armanterzyan/Code/Learning/Stock_Screener')

from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from etl_yfinance import db, extract, transform, load
import pandas as pd

# Function to get available data and push it to XCom
def get_available_data(**kwargs):
    conn = db.get_db_connection()
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
    
    # Apply the extraction logic
    extract_res = available_data.apply(extract.extract, axis=1)
    extract_res = pd.concat(extract_res.tolist(), ignore_index=True)
    
    # Convert the extracted data to JSON
    extracted_data_json = extract_res.to_json(orient='split')
    
    # Push the extracted data to XCom (as JSON)
    kwargs['ti'].xcom_push(key='extracted_data', value=extracted_data_json)
    return extracted_data_json

# Function to transform data, pulling from XCom
def transform_data(**kwargs):
    ti = kwargs['ti']
    
    # Pull the extracted data from XCom (as JSON)
    extracted_data_json = ti.xcom_pull(task_ids='extract_data', key='extracted_data')
    
    # Convert the JSON back to a DataFrame
    extracted_data = pd.read_json(extracted_data_json, orient='split')
    print(extracted_data.head())
    
    # Apply the transformation logic
    transformed_data = transform.transform(extracted_data)
    print(transformed_data.head())
    
    # Convert the transformed data to JSON
    transformed_data_json = transformed_data.to_json(orient='split')
    
    # Push the transformed data to XCom (as JSON)
    kwargs['ti'].xcom_push(key='transformed_data', value=transformed_data_json)
    return transformed_data_json

# Function to load data into the database, pulling from XCom
def load_data(**kwargs):
    ti = kwargs['ti']
    
    # Pull the transformed data from XCom (as JSON)
    transformed_data_json = ti.xcom_pull(task_ids='transform_data', key='transformed_data')

    # Convert the JSON back to a DataFrame
    transformed_data = pd.read_json(transformed_data_json, orient='split')
    print(transformed_data.head())
    transformed_data['performance_date'] = pd.to_datetime(transformed_data['performance_date'], unit='ms')


    # Database connection and insert query
    conn = db.get_db_connection()
    insert_query = """
        INSERT INTO index_performance (index_id, metric_id, performance_date, metric_value)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (index_id, metric_id, performance_date) 
        DO NOTHING;
    """
    load.insert_data_to_db(transformed_data, insert_query, conn)
    conn.close()

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 3, 2),  # Adjust the start date as per your needs
}

# Define the DAG
with DAG(
    'etl_process',  # DAG name
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

    # Task to transform data
    task_transform_data = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
        provide_context=True,  # Make sure context is provided for XCom
    )

    # Task to load data into the database
    task_load_data = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
        provide_context=True,  # Make sure context is provided for XCom
    )

    # Set task dependencies (task order)
    task_get_available_data >> task_extract_data >> task_transform_data >> task_load_data