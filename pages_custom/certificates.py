import streamlit as st
from database.connection import fetch_data
from modules.certificate import generate_certificate # Assuming this is your generator function

def render():
    st.title("🎓 My Achievement Certificates")
    
    # Ensure user is logged in
    if "user" not in st.session_state or st.session_state.user is None:
        st.warning("Please login to view your certificates.")
        return

    user_id = st.session_state.user.get('id')
    default_username = st.session_state.user.get('username')

    # Allow the user to input/customize their preferred name for the certificate
    st.subheader("Customize Your Certificate Name")
    custom_name = st.text_input(
        "Enter your full name as you want it to appear on the certificate:", 
        value=default_username
    )

    st.markdown("---")

    # Query: Fetch only quizzes that the user has submitted (attempts)
    query = f"""
        SELECT quiz_title, percentage, attempted_at 
        FROM quiz_attempts 
        WHERE user_id = {user_id}
        ORDER BY attempted_at DESC
    """
    
    df = fetch_data(query)

    if df is not None and not df.empty:
        st.write(f"Hello **{default_username}**, here are the certificates for your submitted quizzes:")
        
        # Determine the final name to print (fallback to default username if blank)
        name_to_print = custom_name.strip() if custom_name.strip() else default_username

        for _, row in df.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                col1.subheader(f"✅ {row['quiz_title']}")
                col1.caption(f"Submitted on: {row['attempted_at']} | Score: {row['percentage']}%")
                
                # Generate the certificate using the customized name input
                cert_bytes = generate_certificate(name_to_print, row['quiz_title'], row['percentage'])
                
                col2.download_button(
                    label="Download Certificate",
                    data=cert_bytes,
                    file_name=f"Certificate_{row['quiz_title'].replace(' ', '_')}.png",
                    mime="image/png",
                    key=f"dl_{row['quiz_title']}" # Unique key required for loops in Streamlit
                )
    else:
        st.info("You haven't submitted any quizzes yet. Head to the **Quiz Portal** to get started!")