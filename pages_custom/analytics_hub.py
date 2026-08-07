import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Ensure root path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.connection import fetch_data


@st.cache_data(ttl=60, show_spinner=False)
def load_analytics_data():
    """Fetches submission and user data for analytical reporting."""
    query = """
        SELECT 
            s.id AS submission_id,
            s.user_id,
            u.username,
            s.quiz_id,
            q.title AS quiz_title,
            s.score,
            s.total_questions,
            (s.score / NULLIF(s.total_questions, 0)) * 100 AS percentage,
            s.time_taken_seconds,
            s.submitted_at
        FROM quiz_submissions s
        LEFT JOIN users u ON s.user_id = u.id
        LEFT JOIN quizzes q ON s.quiz_id = q.id
    """
    df = fetch_data(query)
    return df if df is not None else pd.DataFrame()


def render():
    st.markdown("## 📊 Academic Performance & Analytics")
    st.caption("Real-time telemetry and student evaluation metrics across all conducted assessments.")

    df = load_analytics_data()

    if df.empty:
        st.warning("⚠️ No quiz submission data found in the database yet. Run a few quizzes to populate analytics.")
        return

    # Clean data types
    df["percentage"] = pd.to_numeric(df["percentage"], errors="coerce").fillna(0)
    df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0)
    df["time_taken_seconds"] = pd.to_numeric(df["time_taken_seconds"], errors="coerce").fillna(0)

    # --- TOP CONTROLS & FILTER BAR ---
    st.markdown("---")
    c_filter1, c_filter2 = st.columns([1.5, 1])

    with c_filter1:
        quizzes = ["All Quizzes"] + list(df["quiz_title"].dropna().unique())
        selected_quiz = st.selectbox("🎯 Filter by Quiz/Assessment:", quizzes)

    with c_filter2:
        pass_mark = st.slider("🎯 Set Target Benchmark Pass Score (%)", min_value=30, max_value=90, value=60, step=5)

    # Apply Quiz Filter
    if selected_quiz != "All Quizzes":
        filtered_df = df[df["quiz_title"] == selected_quiz].copy()
    else:
        filtered_df = df.copy()

    # --- KPI METRIC CARDS ---
    total_participants = filtered_df["user_id"].nunique()
    total_attempts = len(filtered_df)
    passed_students = filtered_df[filtered_df["percentage"] >= pass_mark]["user_id"].nunique()
    pass_rate = (passed_students / total_participants * 100) if total_participants > 0 else 0
    avg_score = filtered_df["percentage"].mean() if not filtered_df.empty else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("👥 Total Participants", f"{total_participants:,}")
    m2.metric("📝 Total Attempts", f"{total_attempts:,}")
    m3.metric(f"✅ Scored ≥ {pass_mark}%", f"{passed_students:,}", f"{pass_rate:.1f}% Pass Rate")
    m4.metric("📊 Average Score", f"{avg_score:.1f}%")

    st.markdown("---")

    # --- ROW 1: TOP RANKERS & PASS/FAIL BENCHMARK ---
    col_rank, col_bench = st.columns([1.2, 1], gap="large")

    with col_rank:
        st.subheader("🏆 Top Performance Leaderboard")

        # Aggregate highest percentage per student
        top_students = (
            filtered_df.groupby("username")
            .agg(
                max_score=("percentage", "max"),
                avg_score=("percentage", "mean"),
                quizzes_taken=("quiz_id", "count")
            )
            .reset_index()
            .sort_values(by="max_score", ascending=False)
            .head(10)
        )

        fig_rank = px.bar(
            top_students,
            x="max_score",
            y="username",
            orientation="h",
            text="max_score",
            color="max_score",
            color_continuous_scale="Purples",
            labels={"max_score": "Highest Score (%)", "username": "Student Roll/Name"},
            title="Top 10 High Scorers"
        )
        fig_rank.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_rank.update_layout(
            yaxis={"categoryorder": "total ascending"},
            showlegend=False,
            height=380,
            margin=dict(l=0, r=20, t=40, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc")
        )
        st.plotly_chart(fig_rank, use_container_width=True)

    with col_bench:
        st.subheader(f"🎯 Target Benchmark Status ({pass_mark}%)")

        passed_count = (filtered_df["percentage"] >= pass_mark).sum()
        failed_count = len(filtered_df) - passed_count

        donut_data = pd.DataFrame({
            "Status": [f"Above Benchmark (≥{pass_mark}%)", f"Below Benchmark (<{pass_mark}%)"],
            "Count": [passed_count, failed_count]
        })

        fig_donut = px.pie(
            donut_data,
            names="Status",
            values="Count",
            hole=0.55,
            color="Status",
            color_discrete_map={
                f"Above Benchmark (≥{pass_mark}%)": "#10b981",
                f"Below Benchmark (<{pass_mark}%)": "#ef4444"
            }
        )
        fig_donut.update_traces(textinfo="percent+label", pull=[0.05, 0])
        fig_donut.update_layout(
            height=380,
            showlegend=False,
            margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc")
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("---")

    # --- ROW 2: PARTICIPATION DISTRIBUTION & SPEED VS SCORE ---
    col_part, col_speed = st.columns([1, 1.2], gap="large")

    with col_part:
        st.subheader("📚 Quiz Participation Breakdown")

        part_df = (
            df.groupby("quiz_title")["user_id"]
            .nunique()
            .reset_index()
            .rename(columns={"user_id": "participants", "quiz_title": "Quiz"})
        )

        fig_part = px.pie(
            part_df,
            names="Quiz",
            values="participants",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_part.update_layout(
            height=360,
            margin=dict(l=0, r=0, t=30, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc")
        )
        st.plotly_chart(fig_part, use_container_width=True)

    with col_speed:
        st.subheader("⏱️ Speed vs. Accuracy Analysis")

        filtered_df["time_min"] = (filtered_df["time_taken_seconds"] / 60).round(2)

        fig_scatter = px.scatter(
            filtered_df,
            x="time_min",
            y="percentage",
            color="quiz_title",
            size="score",
            hover_data=["username"],
            labels={
                "time_min": "Time Taken (Minutes)",
                "percentage": "Score Percentage (%)",
                "quiz_title": "Quiz"
            },
            title="Time Efficiency per Submission"
        )
        fig_scatter.add_hline(y=pass_mark, line_dash="dash", line_color="#10b981", annotation_text="Benchmark")
        fig_scatter.update_layout(
            height=360,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc")
        )
        st.plotly_chart(fig_scatter, use_container_width=True)


if __name__ == "__main__":
    render()