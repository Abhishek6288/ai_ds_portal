import pandas as pd
from utils.db import get_db_connection

def get_connection():
    """ 
    Returns an active connection object to the MySQL database.
    Dynamically routes to Aiven (via secrets) on Streamlit Cloud,
    or falls back to localhost when testing offline.
    """
    return get_db_connection()

def fetch_data(query, params=None):
    """ Executes SELECT queries and returns a Pandas DataFrame. """
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            return None
            
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()

def execute_query(query, params=None):
    """ Executes INSERT, UPDATE, or DELETE queries with parameterized inputs. """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        if conn is None:
            raise Exception("Failed to establish database connection.")
            
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database Error: {e}")
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()