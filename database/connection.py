import pandas as pd
import streamlit as st
import mysql.connector

def get_connection():
    """ Connects to Aiven MySQL using Streamlit secrets. """
    try:
        db_config = st.secrets["mysql"]
        conn = mysql.connector.connect(
            host=db_config["host"],
            port=int(db_config.get("port", 28437)),
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
            ssl_disabled=False
        )
        return conn
    except Exception as e:
        st.error(f"❌ Failed to connect to Aiven MySQL: {e}")
        print(f"❌ Aiven Connection Error: {e}")
        return None

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