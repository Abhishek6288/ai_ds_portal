import streamlit as st
import pandas as pd
from database.connection import execute_query, fetch_data

def render():
    st.title("✍️ FY UG Assessment Portal")
    
    user = st.session_state.get("user", {})
    user_id = user.get("id")
    username = user.get("username", "Student")
    
    st.caption("🚀 Target Audience: First-Year Undergraduate AI & Data Science Students")
    st.markdown("---")

    # --- SESSION STATE FOR QUIZ NAVIGATION ---
    if "active_quiz_id" not in st.session_state:
        st.session_state.active_quiz_id = None

    # Fetch available quizzes from database
    quizzes_df = fetch_data("SELECT * FROM quizzes;")

    if quizzes_df is None or quizzes_df.empty:
        st.info("📌 No assessments are currently available. Please check back later when faculty publishes a quiz.")
        return

    # --- VIEW 1: QUIZ SELECTION CARD GRID (If no quiz is active) ---
    if st.session_state.active_quiz_id is None:
        st.subheader("📚 Available Assessments")
        st.write("Select a module below to launch your exam environment.")
        st.markdown("<br>", unsafe_allow_html=True)

        # Create a 2-column or 3-column layout for cards
        cols = st.columns(2)
        
        for idx, row in quizzes_df.iterrows():
            quiz_id = row['id']
            title = row['quiz_title']
            duration = row.get('duration_minutes', 30)
            passing = row.get('passing_score', 50)

            # Count questions for this quiz
            count_df = fetch_data("SELECT COUNT(*) AS total FROM questions WHERE quiz_id = %s;", (quiz_id,))
            q_count = count_df.iloc[0]['total'] if count_df is not None and not count_df.empty else 0

            # Place cards alternately in columns
            with cols[idx % 2]:
                with st.container(border=True):
                    st.markdown(f"### ⚡ {title}")
                    st.markdown(f"📝 **Questions:** {q_count}")
                    st.markdown(f"⏱️ **Duration:** {duration} Mins")
                    st.markdown(f"🎯 **Passing Score:** {passing}%")
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    if st.button(f"🚀 Start Assessment", key=f"start_quiz_{quiz_id}", use_container_width=True):
                        st.session_state.active_quiz_id = quiz_id
                        st.rerun()

    # --- VIEW 2: ACTIVE QUIZ TAKING INTERFACE ---
    else:
        active_id = st.session_state.active_quiz_id
        quiz_row = quizzes_df[quizzes_df['id'] == active_id]

        if quiz_row.empty:
            st.error("Quiz not found.")
            if st.button("⬅️ Back to Quizzes"):
                st.session_state.active_quiz_id = None
                st.rerun()
            return

        quiz_info = quiz_row.iloc[0]
        selected_quiz_title = quiz_info['quiz_title']
        duration = quiz_info.get('duration_minutes', 30)
        passing_score = quiz_info.get('passing_score', 50)

        # Back button to return to card view
        if st.button("⬅️ Back to All Assessments"):
            st.session_state.active_quiz_id = None
            st.rerun()

        st.markdown("---")
        st.subheader(f"📚 Active Assessment: {selected_quiz_title}")
        st.info(f"⏱️ Recommended Time: {duration} Mins | 🎯 Passing Score: {passing_score}%")
        st.markdown("<br>", unsafe_allow_html=True)

        # Fetch questions for this specific quiz
        questions_df = fetch_data("SELECT * FROM questions WHERE quiz_id = %s;", (active_id,))

        if questions_df is None or questions_df.empty:
            st.warning("⚠️ This quiz does not have any questions added yet.")
            return

        submission_key = f"submitted_{user_id}_quiz_{active_id}"
        if submission_key not in st.session_state:
            st.session_state[submission_key] = False

        with st.form(f"quiz_form_{active_id}"):
            user_responses = {}
            for idx, row in questions_df.iterrows():
                q_id = row['id']
                q_num = idx + 1
                question_text = row['question_text']
                
                options = [row['option_a'], row['option_b']]
                if row['option_c'] and str(row['option_c']).strip() != "":
                    options.append(row['option_c'])
                if row['option_d'] and str(row['option_d']).strip() != "":
                    options.append(row['option_d'])

                st.markdown(f"**Q{q_num}.** {question_text}")
                
                user_responses[q_id] = st.radio(
                    label=f"q_{q_id}_label",
                    options=options,
                    key=f"student_q_{q_id}",
                    index=None,
                    label_visibility="collapsed"
                )
                st.markdown("---")

            submit_btn = st.form_submit_button("Submit Quiz Answers 🚀", use_container_width=True)

        # --- SCORE PROCESSING LOGIC ---
        if submit_btn:
            unanswered = [row['id'] for _, row in questions_df.iterrows() if user_responses[row['id']] is None]
            
            if unanswered:
                st.error(f"⚠️ Please answer all questions before submitting! You have missed {len(unanswered)} question(s).")
            else:
                st.session_state[submission_key] = True
                correct_count = 0
                total_questions = len(questions_df)

                st.subheader("📊 Quiz Results & Review")

                for idx, row in questions_df.iterrows():
                    q_id = row['id']
                    q_num = idx + 1
                    selected_text = user_responses[q_id]
                    
                    correct_letter = row['correct_option'].strip().upper()
                    option_mapping = {
                        "A": row['option_a'],
                        "B": row['option_b'],
                        "C": row['option_c'],
                        "D": row['option_d']
                    }
                    correct_text = option_mapping.get(correct_letter)

                    if selected_text == correct_text:
                        correct_count += 1
                        st.success(f"✅ **Q{q_num}: Correct!** (Your answer: {selected_text})")
                    else:
                        st.error(f"❌ **Q{q_num}: Incorrect.** (Your answer: {selected_text} | Correct answer: **{correct_text}**)")

                final_percentage = round((correct_count / total_questions) * 100, 1)
                
                st.markdown("---")
                if final_percentage >= passing_score:
                    st.balloons()
                    st.success(f"🎉 **Congratulations!** You passed with **{correct_count}/{total_questions}** ({final_percentage}%).")
                else:
                    st.warning(f"📖 **Keep Learning!** You scored **{correct_count}/{total_questions}** ({final_percentage}%). Required to pass: {passing_score}%.")

                # Save score to MySQL history with quiz_id included
                if user_id:
                    try:
                        insert_query = """
                            INSERT INTO quiz_attempts (user_id, quiz_id, quiz_title, score, max_score, percentage) 
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        execute_query(insert_query, (user_id, active_id, selected_quiz_title, correct_count, total_questions, final_percentage))
                        st.caption("✅ Score successfully saved to your portal history.")
                    except Exception as e:
                        st.caption(f"ℹ️ Score processed successfully. (Log info: {e})")