import mysql.connector
from mysql.connector import pooling
import streamlit as st

# @st.cache_resource ensures the pool is created ONLY ONCE when the app starts,
# and reused across all 200 connected students.
@st.cache_resource
def get_connection_pool():
    try:
        if "mysql" in st.secrets:
            cfg = st.secrets["mysql"]
            return pooling.MySQLConnectionPool(
                pool_name="aiven_pool",
                pool_size=20,             # Maintains up to 20 reusable DB connections
                pool_reset_session=True,  # Cleans up temporary states when connections return to pool
                host=cfg["host"],
                port=int(cfg["port"]),
                user=cfg["user"],
                password=cfg["password"],
                database=cfg["database"],
                connect_timeout=10
            )
        else:
            return pooling.MySQLConnectionPool(
                pool_name="local_pool",
                pool_size=10,
                pool_reset_session=True,
                host="localhost",
                port=3306,
                user="root",
                password="",
                database="defaultdb"
            )
    except mysql.connector.Error as err:
        st.error(f"❌ Failed to initialize database connection pool: {err}")
        return None

def get_db_connection():
    """Fetches an active, pre-established connection from the pool."""
    pool = get_connection_pool()
    if pool:
        return pool.get_connection()
    return None