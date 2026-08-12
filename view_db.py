from database.connection import fetch_data

print("--- QUIZZES ---")
quizzes = fetch_data("SELECT * FROM quizzes;")
print(quizzes)

print("\n--- QUESTIONS ---")
questions = fetch_data("SELECT * FROM questions;")
print(questions)
