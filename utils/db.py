import os
import mysql.connector
import streamlit as st

def get_db_connection():
    """
    Connects to Aiven when hosted on Streamlit Cloud (via secrets),
    or falls back to local MySQL/environment variables when developing.
    """
    try:
        # 1. Check Streamlit Secrets (Streamlit Cloud or local secrets.toml)
        if "mysql" in st.secrets:
            cfg = st.secrets["mysql"]
            return mysql.connector.connect(
                host=cfg["host"],
                port=int(cfg["port"]),
                user=cfg["user"],
                password=cfg["password"],
                database=cfg["database"],
                connect_timeout=10
            )
        
        # 2. Fallback for local testing/Codespaces without secrets
        else:
            return mysql.connector.connect(
                host="localhost",
                port=3306,
                user="root",
                password="",
                database="defaultdb"
            )

    except mysql.connector.Error as err:
        st.error(f"❌ Database connection error: {err}")
        return None