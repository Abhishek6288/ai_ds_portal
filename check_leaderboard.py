from database.connection import fetch_data

df = fetch_data("SELECT * FROM quiz_attempts;")
if df is not None:
    print("🏆 Data inside quiz_attempts:")
    print(df)
else:
    print("Table is empty or could not be read.")
