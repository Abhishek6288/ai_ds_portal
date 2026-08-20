from database.connection import execute_query, fetch_data

def main():
    print("--- Fetching all users ---")
    users_df = fetch_data("create table quiz_submissions")
    print(users_df)

if __name__ == "__main__":
    main()

