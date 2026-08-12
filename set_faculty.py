from database.connection import execute_query

# Update abhishek's role to Faculty in the database
query = "UPDATE users SET role = 'Faculty' WHERE username = 'abhishek';"
execute_query(query)
print("✅ Successfully updated abhishek to Faculty role in the database!")
