from database.connection import fetch_data

df = fetch_data("SELECT username, role FROM users WHERE username = 'abhishek';")
print(df)
