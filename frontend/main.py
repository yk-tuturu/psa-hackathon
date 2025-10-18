import streamlit as st
import time
import requests

BACKEND_URL = ""

st.set_page_config(page_title="Chatbot", page_icon="💬", layout="centered")

st.title("💬 PSA Network Insights Dashboard")

report_res = requests.get(f"{BACKEND_URL}/report").json()
token_res = requests.get(f"{BACKEND_URL}/embed-token").json()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history with custom icons
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Type your message..."):
    # Add user message
    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

        payload = {
            "history": messages,  # entire conversation so far
            "message": prompt     # new user message
        }

        try:
            res = requests.post(BACKEND_URL, json=payload, timeout=30)
            if res.status_code == 200:
                response = res.json().get("reply", "No reply received")
            else:
                response = f"Error {res.status_code}: {res.text}"
        except Exception as e:
            response = f"Error: {e}"

        # Optional: simulate typing delay
        time.sleep(0.5)
        message_placeholder.markdown(response)

    # Add assistant message
    st.session_state["messages"].append({"role": "assistant", "content": response})