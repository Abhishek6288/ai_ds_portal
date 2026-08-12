from database.connection import execute_query

# SQL statements to create the missing tables
queries = [
    """
    CREATE TABLE IF NOT EXISTS quizzes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        quiz_title VARCHAR(255) NOT NULL,
        duration_minutes INT NOT NULL DEFAULT 30,
        passing_score INT NOT NULL DEFAULT 50,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS questions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        quiz_id INT NOT NULL,
        question_text TEXT NOT NULL,
        option_a VARCHAR(255) NOT NULL,
        option_b VARCHAR(255) NOT NULL,
        option_c VARCHAR(255),
        option_d VARCHAR(255),
        correct_option VARCHAR(10) NOT NULL,
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
    );
    """
]

for q in queries:
    execute_query(q)

print("✅ Tables 'quizzes' and 'questions' created successfully!")
