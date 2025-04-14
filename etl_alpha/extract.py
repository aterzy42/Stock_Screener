import pandas as pd
import requests

# Function to fetch and process data from Alpha Vantage
def extract(row,api_key):
    """
    Pull data for chosen economic indicators from Alpha Vantage.
    If the variable is posted annually we will fill in all the months 
    of that particular year with that value. 

    Return:
    Dataframe with indicator_id,date,value, and source (Alpha Vantage)
    
    
    """
    indicator_id = row['indicator_id']
    indicator_name = row['indicator_name']

    url = f'https://www.alphavantage.co/query?function={indicator_name}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()

    if 'data' not in data:  # Handle API errors
        print(f"Error fetching {indicator_name}: {data.get('error', 'Unknown error')}")
        return pd.DataFrame()  # Return an empty DataFrame if API fails

    all_data = []

    if data.get('interval') == 'annual':  
        for entry in data['data']:
            year = entry['date'][:4]
            value = entry['value']
            for month in range(1, 13):
                date = f"{year}-{month:02d}-01"
                all_data.append({'indicator_id': indicator_id,
                                 'data_date': date, 'indicator_value': value})
    else:  
        for entry in data['data']:
            all_data.append({'indicator_id': indicator_id,
                             'data_date': entry['date'], 'indicator_value': entry['value']})

    df = pd.DataFrame(all_data)
    df['indicator_value'] = pd.to_numeric(df['indicator_value'], errors='coerce')  # Ensure numeric values
    df['data_source'] = 'Alpha'
    return df