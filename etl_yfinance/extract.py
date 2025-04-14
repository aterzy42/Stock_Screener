import pandas as pd
import yfinance as yf

def extract(row):
    """
    Pull values for each ticker currently in market_indices
    between start and end date. 
     
    Returns:
    Dataframe
    """  
    ticker = row['yfinance_ticker']
    index_id = row['index_id']
    metric_id = row['metric_id']
    
    # Handle the start_date based on max_date
    if pd.isna(row['max_date']):
        start_date = '2000-01-01'
    else:
        start_date = pd.to_datetime(row['max_date'],unit='ms')
        
    end_date = pd.to_datetime('today').strftime("%Y-%m-%d")

    # Desired metric name (not used in the current code but may be used later)
    desired_metric = row['metric_name']

    # Download the data
    data = yf.download(ticker, start=start_date, end=end_date)

    # Check if data is returned
    if data.empty:
        print(f"No data found for ticker: {ticker}")
        return pd.DataFrame()  # Return an empty DataFrame if no data is found

    # Process the data
    formatted_data = data[[desired_metric]].reset_index()  # Resetting index to get 'Date' as a column
    formatted_data[desired_metric] = formatted_data[desired_metric].round(2)

    # Rename columns
    formatted_data.columns = ['performance_date', 'metric_value']
    formatted_data['index_id'] = index_id
    formatted_data['metric_id'] = metric_id

    formatted_data = formatted_data[['index_id', 'metric_id', 'performance_date', 'metric_value']]

    # Return the formatted data as a DataFrame
    return formatted_data