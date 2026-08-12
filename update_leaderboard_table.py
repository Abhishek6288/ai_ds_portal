from database.connection import execute_query

# Update table to track specific quiz IDs
execute_query("""
    CREATE TABLE IF NOT EXISTS quiz_attempts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        quiz_id INT NOT NULL,
        quiz_title VARCHAR(255) NOT NULL,
        score INT NOT NULL,
        max_score INT NOT NULL,
        percentage DECIMAL(5,2) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
print("✅ Leaderboard tracking table ready!")
