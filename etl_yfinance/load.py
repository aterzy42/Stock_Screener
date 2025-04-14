


def insert_data_to_db(df, insert_query, conn):
    """
    Insert data from a DataFrame into the database.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data to be inserted.
    insert_query (str): SQL insert query to execute.
    conn (psycopg2.connection): A connection object to the database.
    
    Returns:
    None
    """
    try:
        # Create a cursor from the connection
        cur = conn.cursor()

        # Insert data for each row in the DataFrame
        for index, row in df.iterrows():
            try:
                # Extract values from each row
                values = (row['index_id'], row['metric_id'], row['performance_date'], row['metric_value'])

                # Execute the insert query with the extracted values
                cur.execute(insert_query, values)

            except Exception as e:
                # Handle any error during the insert (e.g., duplicate entry)
                print(f"Error inserting row {row}: {e}. Skipping insert.")

        # Commit the transaction after inserting all rows
        conn.commit()

        print('Data insert complete.')

    except Exception as e:
        print(f"Error while inserting data into the database: {e}")
    
    finally:
        # Ensure the cursor is closed after execution
        cur.close()
