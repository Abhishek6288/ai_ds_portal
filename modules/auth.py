import bcrypt
from database.connection import fetch_data

def check_password(password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

# 🚨 MUST BE NAMED EXACTLY: authenticate_user
def authenticate_user(identifier: str, password: str):
    """ Authenticates a user against MySQL database. """
    query = "SELECT * FROM users WHERE username = %s OR email = %s"
    df = fetch_data(query, (identifier, identifier))
    
    # Safety check for DataFrame
    if df is None or df.empty:
        return None, "User not found with provided credentials."
    
    # Extract row
    user_row = df.iloc[0]
    db_hash = str(user_row['password_hash'])
    
    # Validate password
    if check_password(password, db_hash):
        user_info = {
            "id": int(user_row['id']),
            "username": str(user_row['username']),
            "email": str(user_row['email']),
            "role": str(user_row['role'])
        }
        return user_info, "Login successful!"
    else:
        return None, "Invalid password."
    
import bcrypt
from database.connection import fetch_data, execute_query

def hash_password(password: str) -> str:
    """Hashes a plain text password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def register_user(username: str, email: str, password: str, role: str = "Student"):
    """
    Checks for duplicates, hashes the password, and inserts the record into MySQL.
    """
    # 1. Prevent duplicate usernames or emails
    check_query = "SELECT id FROM users WHERE username = %s OR email = %s"
    existing = fetch_data(check_query, (username, email))
    
    if existing is not None and not existing.empty:
        return False, "Username or Email is already registered."
    
    # 2. Hash raw password securely
    hashed_pwd = hash_password(password)
    
    # 3. Store record in MySQL
    insert_query = """
        INSERT INTO users (username, email, password_hash, role)
        VALUES (%s, %s, %s, %s)
    """
    try:
        execute_query(insert_query, (username, email, hashed_pwd, role))
        return True, "Registration successful!"
    except Exception as e:
        return False, f"Database insert failed: {str(e)}"

def authenticate_user(identifier: str, password: str):
    """ Authenticates a user against the MySQL users table. """
    query = "SELECT * FROM users WHERE username = %s OR email = %s"
    df = fetch_data(query, (identifier, identifier))
    
    if df is None or df.empty:
        return None, "User not found."
    
    user_row = df.iloc[0]
    db_hash = str(user_row['password_hash'])
    
    if check_password(password, db_hash):
        user_info = {
            "id": int(user_row['id']),
            "username": str(user_row['username']),
            "email": str(user_row['email']),
            "role": str(user_row['role'])
        }
        return user_info, "Login successful!"
    else:
        return None, "Invalid password."