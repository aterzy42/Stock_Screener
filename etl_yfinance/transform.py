import pandas as pd

def grouping(df):
    """
    Helper function to get min and max performance date
    for each index.
    
    Parameters:
    name (df): Dataframe with performance values for each index
    
    Returns:
    Groupby object of min and max date of each of the indices.
    """
    df_grouped = df.groupby(['index_id', 'metric_id'])['performance_date'].agg(['min', 'max']).reset_index().rename(columns={'min': 'min_day', 'max': 'max_day'})
    return df_grouped


def start_end(row):
    """
    Helper function to get the performance on the 15th of
    each month of performance for each index - metric pair.
    
    Parameters:
    name (row): Row of groupby object with min and max performance date of 
                each index - metric pair.
    
    Returns:
    Dataframe with index-metric pair , date (15th),metric value.
    """
    # Ensure 'min_day' and 'max_day' are datetime
    row['min_day'] = pd.to_datetime(row['min_day'], errors='coerce', unit='ms')
    row['max_day'] = pd.to_datetime(row['max_day'], errors='coerce', unit='ms')
    
    # Check if the conversion was successful
    if pd.isnull(row['min_day']) or pd.isnull(row['max_day']):
        raise ValueError(f"Invalid date found: min_day={row['min_day']}, max_day={row['max_day']}")


    # Create a date range for the 15th of each month within the range of the performance_date
    start_date = row['min_day'].replace(day=1)  # Start from the first day of the month
    if row['max_day'].day < 15:
        end_date = (row['max_day'].replace(day=1) - pd.DateOffset(months=1)).replace(day=1)
    else:
        end_date = row['max_day'].replace(day=1)  # End at the first day of the last month
    dates = pd.date_range(start=start_date, end=end_date, freq='MS') + pd.DateOffset(days=14)  # 15th of each month

    # Generate all combinations of index_id, metric_id, and the 15th of each month
    combinations = pd.MultiIndex.from_product(
        [[row['index_id']], [row['metric_id']], dates],
        names=['index_id', 'metric_id', 'performance_date']
    )
    
    # # Create a new DataFrame with all combinations of index_id, metric_id, and the 15th of each month
    df_extended = pd.DataFrame(index=combinations).reset_index()
    return(df_extended)


def forward_fill_15(df1,df2):
    """
    Fill in 15th of month if it happened to be a weekend or holiday.
    
    Parameters:
    name (df1,df2): Dataframes with performance values and one with 15ths.
    
    Returns:
    Merged df with just performance of forward filled values on 15th of each month.
    """
    # Ensure 'performance_date' is datetime in both dataframes
    df1['performance_date'] = pd.to_datetime(df1['performance_date'], errors='coerce', unit='ms')
    df2['performance_date'] = pd.to_datetime(df2['performance_date'], errors='coerce', unit='ms')

    # Merge with original DataFrame on index_id, metric_id, and performance_date
    df_merged = pd.merge(df1, df2, on=['index_id', 'metric_id', 'performance_date'], how='outer')
    df_merged = df_merged.sort_values(by=['index_id', 'metric_id', 'performance_date'])
    
    # Forward fill the missing metric_value
    df_merged['metric_value'] = df_merged.groupby(['index_id', 'metric_id'])['metric_value'].ffill()
    df_merged = df_merged[df_merged['performance_date'].dt.day == 15]
    return(df_merged)

def transform(df):
    extract_grouped = grouping(df)
    req_dates = extract_grouped.apply(start_end,axis=1)
    req_dates = pd.concat(req_dates.tolist(), ignore_index=True)
    filled = forward_fill_15(df,req_dates)
    return(filled)