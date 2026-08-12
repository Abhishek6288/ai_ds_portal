import streamlit as st
from database.connection import execute_query, fetch_data

def render():
    st.title("⚙️ Faculty Administration Panel")
    st.caption("Manage quizzes, add questions, and review departmental assessments.")
    st.markdown("---")

    tab_quiz, tab_questions, tab_manage = st.tabs([
        "➕ Create New Quiz", 
        "📝 Add Questions", 
        "👀 Manage & Preview Quizzes"
    ])

    # --- TAB 1: CREATE QUIZ ---
    with tab_quiz:
        st.subheader("Create a New Assessment")
        with st.form("create_quiz_form"):
            quiz_title = st.text_input("Quiz Title", placeholder="e.g. Advanced Python & Pandas")
            duration_mins = st.number_input("Duration (Minutes)", min_value=5, max_value=180, value=30)
            passing_score = st.number_input("Passing Percentage (%)", min_value=10, max_value=100, value=50)
            
            submit_quiz = st.form_submit_button("Publish Quiz")

            if submit_quiz:
                if quiz_title:
                    try:
                        query = "INSERT INTO quizzes (quiz_title, duration_minutes, passing_score) VALUES (%s, %s, %s);"
                        execute_query(query, (quiz_title, duration_mins, passing_score))
                        st.success(f"🎉 Quiz '{quiz_title}' created successfully!")
                    except Exception as e:
                        st.error(f"Error creating quiz: {e}")
                else:
                    st.warning("Please provide a quiz title.")

    # --- TAB 2: ADD QUESTIONS ---
    with tab_questions:
        st.subheader("Add Questions to an Existing Quiz")
        quizzes_df = fetch_data("SELECT id, quiz_title FROM quizzes;")
        
        if quizzes_df is not None and not quizzes_df.empty:
            quiz_options = {row['quiz_title']: row['id'] for _, row in quizzes_df.iterrows()}
            selected_quiz_title = st.selectbox("Select Quiz", list(quiz_options.keys()))
            selected_quiz_id = quiz_options[selected_quiz_title]

            with st.form("add_question_form", clear_on_submit=True):
                question_text = st.text_area("Question Statement")
                opt_a = st.text_input("Option A")
                opt_b = st.text_input("Option B")
                opt_c = st.text_input("Option C")
                opt_d = st.text_input("Option D")
                correct_ans = st.selectbox("Correct Option", ["A", "B", "C", "D"])

                submit_q = st.form_submit_button("Add Question")

                if submit_q:
                    if question_text and opt_a and opt_b:
                        try:
                            q_query = """
                                INSERT INTO questions (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s);
                            """
                            execute_query(q_query, (selected_quiz_id, question_text, opt_a, opt_b, opt_c, opt_d, correct_ans))
                            st.success("✅ Question added successfully!")
                        except Exception as e:
                            st.error(f"Error adding question: {e}")
                    else:
                        st.warning("Please fill out the question text and options A & B.")
        else:
            st.info("No quizzes found. Create a quiz first using the tab above!")

    # --- TAB 3: MANAGE & PREVIEW QUIZZES ---
    with tab_manage:
        st.subheader("📊 Existing Quizzes & Question Preview")
        
        quizzes_df = fetch_data("SELECT * FROM quizzes;")
        
        if quizzes_df is not None and not quizzes_df.empty:
            for _, quiz in quizzes_df.iterrows():
                quiz_id = quiz['id']
                title = quiz['quiz_title']
                duration = quiz['duration_minutes']
                passing = quiz['passing_score']

                # Count questions for this quiz
                count_df = fetch_data("SELECT COUNT(*) AS total FROM questions WHERE quiz_id = %s;", (quiz_id,))
                q_count = count_df.iloc[0]['total'] if count_df is not None and not count_df.empty else 0

                # Create a layout container row for each quiz title and its delete button
                col_title, col_btn = st.columns([3, 1])
                with col_title:
                    st.markdown(f"### 📌 {title}")
                with col_btn:
                    if st.button("🗑️ Delete Quiz", key=f"del_quiz_{quiz_id}", type="primary"):
                        try:
                            # Cleanly delete all dependent rows and the quiz itself
                            execute_query("DELETE FROM questions WHERE quiz_id = %s;", (quiz_id,))
                            execute_query("DELETE FROM quiz_attempts WHERE quiz_id = %s;", (quiz_id,))
                            execute_query("DELETE FROM quizzes WHERE id = %s;", (quiz_id,))
                            
                            st.success(f"Deleted '{title}'")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

                with st.expander(f"View Details & Questions ({q_count} Questions | ⏱️ {duration} mins | 🎯 Pass: {passing}%)"):
                    # Fetch questions for preview
                    questions_df = fetch_data("SELECT * FROM questions WHERE quiz_id = %s;", (quiz_id,))
                    
                    if questions_df is not None and not questions_df.empty:
                        for idx, q in questions_df.iterrows():
                            st.markdown(f"**Q{idx+1}: {q['question_text']}**")
                            st.markdown(f"- A) {q['option_a']}")
                            st.markdown(f"- B) {q['option_b']}")
                            if q['option_c']: st.markdown(f"- C) {q['option_c']}")
                            if q['option_d']: st.markdown(f"- D) {q['option_d']}")
                            st.caption(f"✅ Correct Answer: Option {q['correct_option']}")
                            st.markdown("---")
                    else:
                        st.info("No questions added to this quiz yet.")
                
                st.markdown("---")
        else:
            st.info("No quizzes created yet.")