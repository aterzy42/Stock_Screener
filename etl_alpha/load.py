from psycopg2.extras import execute_values

def batch_insert_data(conn, df, insert_query):
    """
    Inserts data into a PostgreSQL table in batch using the provided query.
    
    Parameters:
        conn (psycopg2 connection): An open connection to the PostgreSQL database.
        extract_res (DataFrame): A pandas DataFrame containing the data to insert.
        insert_query (str): SQL insert query with a %s placeholder for batch values.
    """
    cur = conn.cursor()
    
    data_tuples = list(df.itertuples(index=False, name=None))
    
    execute_values(cur, insert_query, data_tuples)
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("Fast batch insert complete.")
