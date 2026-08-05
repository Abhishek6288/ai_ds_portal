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

    # --- FY UG CURATED QUESTION BANK ---
    fy_quiz_data = [
        {
            "id": 1,
            "topic": "Python Data Structures",
            "question": "Which of the following data structures in Python is **mutable** and defined using square brackets `[]`?",
            "options": ["Tuple", "List", "String", "Set"],
            "answer": "List",
            "explanation": "Lists are mutable (can be changed after creation) and use square brackets `[]`. Tuples use `()` and are immutable."
        },
        {
            "id": 2,
            "topic": "Python Fundamentals",
            "question": "What will be the output of `type(5 / 2)` in Python 3?",
            "options": ["<class 'int'>", "<class 'float'>", "<class 'double'>", "<class 'str'>"],
            "answer": "<class 'float'>",
            "explanation": "In Python 3, division with `/` always returns a float (2.5), whereas floor division `//` returns an integer."
        },
        {
            "id": 3,
            "topic": "Basic SQL",
            "question": "Which SQL keyword is used to remove duplicate records from the query result?",
            "options": ["UNIQUE", "DISTINCT", "REMOVE", "GROUP"],
            "answer": "DISTINCT",
            "explanation": "`SELECT DISTINCT column_name FROM table;` returns only unique values, eliminating duplicate rows."
        },
        {
            "id": 4,
            "topic": "Foundational Statistics",
            "question": "In a dataset of exam scores `[60, 70, 70, 80, 90]`, what is the **mode**?",
            "options": ["70", "74", "80", "60"],
            "answer": "70",
            "explanation": "The mode is the value that appears most frequently in a dataset. Here, 70 appears twice."
        },
        {
            "id": 5,
            "topic": "Data Science Tools",
            "question": "Which Python library is primarily used for multidimensional array operations and numerical computing?",
            "options": ["Pandas", "NumPy", "Seaborn", "Flask"],
            "answer": "NumPy",
            "explanation": "NumPy provides the fundamental `ndarray` object for fast array processing and mathematical computations."
        }
    ]

    # --- QUIZ SUBMISSION STATE ---
    if f"submitted_{user_id}" not in st.session_state:
        st.session_state[f"submitted_{user_id}"] = False

    # --- QUIZ FORM UI ---
    with st.form("fy_ug_quiz_form"):
        st.subheader("📚 Quiz: Intro to Python, SQL & Data Essentials")
        st.info("⏱️ Recommended Time: 10 Mins | Passing Score: 70%")
        st.markdown("<br>", unsafe_allow_html=True)
        
        user_responses = {}
        for idx, item in enumerate(fy_quiz_data, start=1):
            st.markdown(f"**Q{idx}. [{item['topic']}]** {item['question']}")
            
            user_responses[item["id"]] = st.radio(
                label=f"q_{item['id']}_label",
                options=item["options"],
                key=f"fy_q_{item['id']}",
                index=None,  # No option pre-selected
                label_visibility="collapsed"
            )
            st.markdown("---")

        submit_btn = st.form_submit_button("Submit Quiz Answers 🚀", use_container_width=True)

    # --- SCORE PROCESSING LOGIC ---
    if submit_btn:
        # Validate that all questions were answered
        unanswered = [q["id"] for q in fy_quiz_data if user_responses[q["id"]] is None]
        
        if unanswered:
            st.error(f"⚠️ Please answer all questions before submitting! (Unanswered Qs: {unanswered})")
        else:
            st.session_state[f"submitted_{user_id}"] = True
            correct_count = 0
            total_questions = len(fy_quiz_data)

            st.subheader("📊 Quiz Results & Review")

            for item in fy_quiz_data:
                q_id = item["id"]
                selected = user_responses[q_id]
                actual = item["answer"]
                
                if selected == actual:
                    correct_count += 1
                    st.success(f"✅ **Q{q_id}: Correct!** (Your answer: {selected})")
                else:
                    st.error(f"❌ **Q{q_id}: Incorrect.** (Your answer: {selected} | Correct answer: **{actual}**)")
                
                with st.expander("💡 View Explanation"):
                    st.write(item["explanation"])

            # Calculation
            final_percentage = round((correct_count / total_questions) * 100, 1)
            
            st.markdown("---")
            if final_percentage >= 70:
                st.balloons()
                st.success(f"🎉 **Congratulations!** You passed with **{correct_count}/{total_questions}** ({final_percentage}%).")
            else:
                st.warning(f"📖 **Keep Learning!** You scored **{correct_count}/{total_questions}** ({final_percentage}%). Review the explanations above and try again.")

            # --- SAVE RESULTS TO MYSQL ---
            if user_id:
                try:
                    insert_query = """
                        INSERT INTO quiz_attempts (user_id, quiz_title, score, max_score, percentage) 
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    execute_query(insert_query, (user_id, "FY UG Intro Quiz", correct_count, total_questions, final_percentage))
                    st.caption("✅ Score successfully saved to your MySQL portal history.")
                except Exception as e:
                    # Fallback in case table schema doesn't exist yet
                    st.caption("ℹ️ Score calculated in session.")