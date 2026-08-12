from database.connection import fetch_data

# Fetch all records from your table
df = fetch_data("SELECT * FROM users")
print(df)