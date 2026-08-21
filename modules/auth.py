import bcrypt
from database.connection import fetch_data, execute_query

def hash_password(password: str) -> str:
    """Hashes a plain text password using bcrypt."""
    clean_pwd = password.strip() if password else ""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(clean_pwd.encode('utf-8'), salt).decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored bcrypt hash."""
    try:
        clean_pwd = password.strip() if password else ""
        return bcrypt.checkpw(clean_pwd.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def register_user(name: str, username: str, email: str, password: str, role: str = "Student"):
    """
    Checks for duplicates, hashes the password, and inserts the record into MySQL with name.
    """
    # Clean inputs to remove accidental spaces
    clean_name = name.strip() if name else ""
    clean_username = username.strip() if username else ""
    clean_email = email.strip() if email else ""
    clean_pwd = password.strip() if password else ""

    # 1. Prevent duplicate usernames or emails
    check_query = "SELECT id FROM users WHERE username = %s OR email = %s"
    existing = fetch_data(check_query, (clean_username, clean_email))
    
    if existing is not None and not existing.empty:
        return False, "Username or Email is already registered."
    
    # 2. Hash raw password securely
    hashed_pwd = hash_password(clean_pwd)
    
    # 3. Store record in MySQL
    insert_query = """
        INSERT INTO users (name, username, email, password_hash, role)
        VALUES (%s, %s, %s, %s, %s)
    """
    try:
        execute_query(insert_query, (clean_name, clean_username, clean_email, hashed_pwd, role))
        return True, "Registration successful!"
    except Exception as e:
        return False, f"Database insert failed: {str(e)}"

def authenticate_user(identifier: str, password: str):
    """ Authenticates a user against the MySQL users table. """
    # Clean the identifier and password from accidental spaces
    clean_identifier = identifier.strip() if identifier else ""
    clean_pwd = password.strip() if password else ""

    query = "SELECT * FROM users WHERE username = %s OR email = %s"
    df = fetch_data(query, (clean_identifier, clean_identifier))
    
    if df is None or df.empty:
        return None, "User not found."
    
    user_row = df.iloc[0]
    db_hash = str(user_row['password_hash'])
    
    if check_password(clean_pwd, db_hash):
        user_info = {
            "id": int(user_row['id']),
            "name": str(user_row['name']) if 'name' in user_row and user_row['name'] else str(user_row['username']),
            "username": str(user_row['username']),
            "email": str(user_row['email']),
            "role": str(user_row['role'])
        }
        return user_info, "Login successful!"
    else:
        return None, "Invalid password."