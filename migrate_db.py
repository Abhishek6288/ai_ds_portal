from database.connection import execute_query

def run_migration():
    print("Connecting to Aiven database to add missing column...")
    try:
        # Adds the quiz_id column to the quiz_attempts table if it doesn't already exist
        execute_query("ALTER TABLE quiz_attempts ADD COLUMN quiz_id INT;")
        print("✅ Success: Added 'quiz_id' column to 'quiz_attempts' table on Aiven!")
    except Exception as e:
        print(f"ℹ️ Note (Column might already exist): {e}")

if __name__ == "__main__":
    run_migration()