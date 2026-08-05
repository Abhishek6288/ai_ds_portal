import mysql.connector
import pandas as pd

# Update with your MySQL credentials
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ai_ds_portal'
}

def get_connection():
    """ Returns a active connection object to the MySQL database. """
    return mysql.connector.connect(**DB_CONFIG)

def fetch_data(query, params=None):
    """ Executes SELECT queries and returns a Pandas DataFrame. """
    conn = None
    try:
        conn = get_connection()
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