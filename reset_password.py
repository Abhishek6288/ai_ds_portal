import bcrypt
from database.connection import execute_query

# Choose the username and the new plain text password you want to set
target_username = "abhishek"
new_plain_password = "abhishek"

# Generate the secure hash
hashed_pw = bcrypt.hashpw(new_plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Update the database
query = "UPDATE users SET password_hash = %s WHERE username = %s;"
execute_query(query, (hashed_pw, target_username))
print(f"✅ Password for '{target_username}' has been reset to: '{new_plain_password}'")
