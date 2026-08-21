from database.connection import execute_query

def run_migration():
    print("Connecting to database to run migrations...")
    
    # 1. Add quiz_id column to quiz_attempts if missing
    try:
        execute_query("ALTER TABLE quiz_attempts ADD COLUMN quiz_id INT;")
        print("✅ Success: Added 'quiz_id' column to 'quiz_attempts' table!")
    except Exception as e:
        print(f"ℹ️ Note ('quiz_id' column might already exist): {e}")

    # 2. Add name column to users table for clean leaderboards and certificates
    try:
        execute_query("ALTER TABLE users ADD COLUMN name VARCHAR(100) AFTER id;")
        print("✅ Success: Added 'name' column to 'users' table!")
    except Exception as e:
        print(f"ℹ️ Note ('name' column might already exist): {e}")

    # 3. Populate existing user names with usernames as fallback
    try:
        execute_query("UPDATE users SET name = username WHERE name IS NULL OR name = '';")
        print("✅ Success: Populated existing user names!")
    except Exception as e:
        print(f"ℹ️ Error populating names: {e}")

if __name__ == "__main__":
    run_migration()