import streamlit as st
import time
import requests
from streamlit_cookies_manager import EncryptedCookieManager
import os
import uuid
from dotenv import load_dotenv
from history import get_user_id, load_history, save_history, clear_history
from api import get_chat_completion
import streamlit.components.v1 as components

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")
USE_BACKEND = True

st.markdown(
    """
    <style>
    .stTextInput > :nth-child(2) {
        position: relative; /* important for absolute positioning */
        border-width: 0px;
    }
    .stTextInput > :nth-child(2):focus-within {
        border-width: 0px;
    }

    .stTextInput > :nth-child(2)::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        z-index: 100;
        border-radius: 0.5rem;
        padding: 1.5px; /* border thickness */
        background: linear-gradient(45deg, #3b82f6, #8b5cf6); /* blue → purple */
        -webkit-mask: 
            linear-gradient(#fff 0 0) content-box, 
            linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events: none;
        opacity: 0;           /* start invisible */
        transition: opacity 0.1s ease-in-out;
    }

    .stTextInput > :nth-child(2):focus-within::before {
        opacity: 1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

# # ---- OPENAI KEY POPUP ----
# @st.dialog("Enter OpenAI API key", width="medium", dismissible=False)
# def getAPIKey():
#     st.write("Just key in anything, this is just for testing")
#     apiKey = st.text_input("", placeholder="Enter API key...", label_visibility="hidden")
#     if st.button("Enter"):
#         saveAPIKey(apiKey)
    
#     if (apiKey):
#         saveAPIKey(apiKey)
        
# def saveAPIKey(key):
#     # Include some verification for the openai key later on
#     st.session_state["apiKey"] = key
#     st.rerun()

# if "apiKey" not in st.session_state:
#     getAPIKey()
#     st.stop()
# else:
#     print(st.session_state["apiKey"])

# Load chat history from db
if "messages" not in st.session_state:
    st.session_state["messages"] = load_history(user_id)

if st.session_state["messages"] == []:
    st.session_state["messages"].append({
        "role": "assistant", 
        "content": "Hi there! This is your PSA Dashboard Assistant! \n\n You can ask me about anything!"})
    save_history(user_id, st.session_state["messages"])

# Set titles
st.set_page_config(page_title="Chatbot", page_icon="💬", layout="wide")
st.title("💬 PSA Network Insights Dashboard")

# attempt to inject css
st.markdown(
    """
    <style>
    .stChatInput {
        border-width: 0px !important;
    }

    .stChatInput::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        z-index: 100;
        border-radius: 1.25rem;
        padding: 1.5px; /* border thickness */
        background: linear-gradient(45deg, #3b82f6, #8b5cf6); /* blue → purple */
        -webkit-mask: 
            linear-gradient(#fff 0 0) content-box, 
            linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events: none;
        opacity: 0;           /* start invisible */
        transition: opacity 0.1s ease-in-out;
    }

    .stChatInput:focus-within::before {
        opacity: 1
    }

    .stMainBlockContainer {
        padding-left: 15rem;
        padding-right: 15rem;
        padding-top: 3rem;
        padding-bottom: 1rem;
    }

    #tabs-bui2-tabpanel-1 {
        max-height: 700px !important;
        height: 700px !important;
        overflow-y: scroll !important;
        padding-left: 2rem;
        padding-right: 2rem;
        font-size: 18px;
        margin-top: 1rem;
    }

    .stTabs button > * {
        font-size: 20px !important;
    }

    .stBottom{
        padding-left: 9rem;
        padding-right: 9rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if st.button("Clear Chat History"):
    clear_history(user_id)
    st.rerun()


HtmlFile = open("powerbi/test.html", 'r', encoding='utf-8')
source_code = HtmlFile.read() 
components.html(source_code, height=700)

# Display sidebar content when toggled

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
            response = get_chat_completion(prompt, st.session_state["messages"])

            time.sleep(0.5)
            message_placeholder.markdown(response)

        # not using backend, placeholder text for frontend testing
        else: 
            response = f"You said **{prompt}**"
            message_placeholder.markdown(response)

    # Add assistant message
    st.session_state["messages"].append({"role": "assistant", "content": response})

    if len(st.session_state["messages"]) > 10:
        st.session_state["messages"].pop(0)
    
    save_history(user_id, st.session_state["messages"])


    





