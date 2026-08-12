from database.connection import fetch_data

df = fetch_data("SHOW TABLES;")
if df is not None:
    print("📁 Tables currently in your Aiven database:")
    print(df)
else:
    print("Could not fetch tables.")
