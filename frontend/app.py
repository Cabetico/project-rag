# frontend/app.py
import streamlit as st
import requests

st.title("E-commerce RAG Chatbot")

# Input box
question = st.text_input("Ask a question:")

# Initialize session state
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "answer" not in st.session_state:
    st.session_state.answer = None

# Send question
if st.button("Send Question"):
    if question:
        response = requests.post(
            "http://python-app:8000/question",
            json={"question": question}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.answer = data["answer"]["answer"]
            st.session_state.conversation_id = data["answer"]["conversation_id"]
        else:
            st.error(f"Error from backend: {response.text}")

# Display answer
if st.session_state.answer:
    st.write("**Answer:**", st.session_state.answer)

    # Feedback buttons
    col1, col2 = st.columns(2)
    if col1.button("👍 Helpful"):
        requests.post(
            "http://python-app:8000/feedback",
            json={"conversation_id": st.session_state.conversation_id, "feedback": 1}
        )
        st.success("Feedback sent 👍")

    if col2.button("👎 Not helpful"):
        requests.post(
            "http://python-app:8000/feedback",
            json={"conversation_id": st.session_state.conversation_id, "feedback": -1}
        )
        st.warning("Feedback sent 👎")
        
# Recent conversations section
limit = st.number_input("How many recent conversations?", min_value=1, max_value=20, value=5, step=1)

backend_url = "http://python-app:8000"

if st.button("Fetch Recent Conversations"):
    response = requests.get(f"{backend_url}/recent?limit={limit}")
    if response.status_code == 200:
        conversations = response.json()
        for conv in conversations:
            with st.expander(f"Conversation {conv['id']} at {conv['timestamp']}"):
                st.write(f"**Q:** {conv['question']}")
                st.write(f"**A:** {conv['answer']}")
                st.write(f"Feedback: {conv['feedback']}")
    else:
        st.error(f"Error fetching conversations: {response.text}")
        
# Feedback statistics
if st.checkbox("Show feedback statistics"):
    response = requests.get(f"{backend_url}/feedback_stats")
    if response.status_code == 200:
        stats = response.json()
        st.metric("👍 Thumbs Up", stats["thumbs_up"])
        st.metric("👎 Thumbs Down", stats["thumbs_down"])
    else:
        st.error(f"Error fetching stats: {response.text}")