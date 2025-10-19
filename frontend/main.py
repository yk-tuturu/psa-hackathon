import streamlit as st
import time
import requests
from streamlit_cookies_manager import EncryptedCookieManager
import os
import uuid
from dotenv import load_dotenv
from history import get_user_id, load_history, save_history, clear_history

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")
USE_BACKEND = False

# Initialize cookie manager
cookies = EncryptedCookieManager(
    prefix="my_app_",  # optional prefix to avoid collisions
    password=os.getenv("DB_PASSWORD")  # must be at least 16 chars
)

# Wait until cookies are loaded
if not cookies.ready():
    st.stop()

# Check if a persistent user_id cookie exists
if "user_id" not in cookies:
    # Create a new user_id and store it in cookies
    user_id = str(uuid.uuid4())
    cookies["user_id"] = user_id
    cookies.save()  # important: save to browser
else:
    user_id = cookies["user_id"]

# Load chat history from db
if "messages" not in st.session_state:
    st.session_state["messages"] = load_history(user_id)

# Set titles
st.set_page_config(page_title="Chatbot", page_icon="💬", layout="centered")
st.title("💬 PSA Network Insights Dashboard")

# Load messages into UI
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Type your message..."):
    # Add user message
    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response
    with st.chat_message("assistant"):
        response = ""
        message_placeholder = st.empty()
        message_placeholder.markdown("...")

        if USE_BACKEND:
            response = send_request(prompt)

            time.sleep(0.5)
            message_placeholder.markdown(response)

        # not using backend, placeholder text for frontend testing
        else: 
            time.sleep(0.5)
            response = f"You said **{prompt}**"
            message_placeholder.markdown(response)

    # Add assistant message
    st.session_state["messages"].append({"role": "assistant", "content": response})
    save_history(user_id, st.session_state["messages"])

# request for chat completion from backend
def send_request(prompt):
    payload = {
        "history": st.session_state["messages"],  # entire conversation so far
        "message": prompt     # new user message
    }

    try:
        res = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
        if res.status_code == 200:
            response = res.json().get("reply", "No reply received")
        else:
            return f"Error {res.status_code}: {res.text}"
    except Exception as e:
        return f"Error: {e}"

