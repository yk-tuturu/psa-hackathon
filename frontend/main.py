import streamlit as st
import time
import requests
from streamlit_cookies_manager import EncryptedCookieManager
import os
import uuid
from dotenv import load_dotenv
from history import get_user_id, load_history, save_history, clear_history
from api import get_chat_completion, compute_intents
import streamlit.components.v1 as components

if os.path.exists(".env"):
    load_dotenv()

def get_secret(key, default=None):
    if os.getenv(key):
        return os.getenv(key)
    if hasattr(st, "secrets") and key in st.secrets:
        return st.secrets[key]
    return default

BACKEND_URL = get_secret("BACKEND_URL")
USE_BACKEND = True

st.set_page_config(page_title="Chatbot", page_icon="💬", layout="wide")

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

# attempt to inject css
st.markdown(
    """
    <style>
    .stChatInput * {
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

    .stButton::before {
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
        transition: opacity 0.07s ease-in-out;
    }

    .stButton:hover::before {
        opacity: 1
    }

    .stChatInput:focus-within::before {
        opacity: 1
    }

    .stMainBlockContainer {
        padding-left: 18rem;
        padding-right: 18rem;
        padding-top: 3rem;
        padding-bottom: 1rem;
    }

    .stChatMessage p, .stChatMessage li {
        font-size: 20px;
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
        padding-left: 12rem;
        padding-right: 12rem;
    }

    .stHeading h1 {
        font-size: 64px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize cookie manager
cookies = EncryptedCookieManager(
    prefix="my_app_", 
    password=get_secret("COOKIE_PASSWORD")
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

if "intent_computed" not in st.session_state:
    st.session_state["intent_computed"] = False

# Set titles
st.title("💬 Navi-Bot")

# Get directory where this script lives
BASE_DIR = os.path.dirname(__file__)

# Construct path to HTML file
html_path = os.path.join(BASE_DIR, "powerbi", "test.html")

# Read HTML
with open(html_path, 'r', encoding='utf-8') as HtmlFile:
    html_content = HtmlFile.read()
    components.html(html_content, height=550)

# OPENAI key popup
@st.dialog("Enter OpenAI API key", width="medium", dismissible=False)
def getAPIKey():
    apiKey = st.text_input("", placeholder="Enter API key...", label_visibility="hidden")
    if st.button("Enter"):
        saveAPIKey(apiKey)

    if (apiKey):
        saveAPIKey(apiKey)
    
def saveAPIKey(key):
    # Include some verification for the openai key later on
    st.session_state["apiKey"] = key
    st.rerun()

if "apiKey" not in st.session_state:
    getAPIKey()
    st.stop()
elif st.session_state["intent_computed"] == False:
    compute_intents()
    st.session_state["intent_computed"] = True

def fresh_chat():
    st.session_state["messages"] = []
    st.session_state["messages"].append({
        "role": "assistant", 
        "content": "Hi there! This is Navi-Bot, your PSA Dashboard Assistant! \n\n You can ask me about anything!",
        "button": True})
    save_history(user_id, st.session_state["messages"])

# Load chat history from db
if "messages" not in st.session_state:
    st.session_state["messages"] = load_history(user_id)

if "button_clicked" not in st.session_state:
    st.session_state["button_clicked"] = None

if st.session_state["messages"] == []:
    fresh_chat()

if st.button("Clear Chat History"):
    clear_history(user_id)
    fresh_chat()


def getAvatar(role):
    if role == "user":
        return os.path.join(BASE_DIR, "images", "person.png")
    elif role == "assistant":
        return os.path.join(BASE_DIR, "images", "bot.png")

def sendMessage(prompt):
    # Add user message
    st.session_state["messages"].append({"role": "user", "content": prompt, "button": False})

    with st.chat_message("user", avatar=getAvatar("user")):
        st.markdown(prompt)
    
    # Get response
    with st.chat_message("assistant", avatar=getAvatar("assistant")):
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
    st.session_state["messages"].append({"role": "assistant", "content": response, "button": False})

    if len(st.session_state["messages"]) > 10:
        st.session_state["messages"].pop(0)
    
    save_history(user_id, st.session_state["messages"])

# Load messages into UI
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"], avatar=getAvatar(msg["role"])):
        st.markdown(msg["content"])
        if (msg["button"]):
            if st.button("Generate dashboard summary"):
                st.session_state["button_clicked"] = "Generate dashboard summary"
            if st.button("What are key actions we can take to improve reliability in our network"):
                 st.session_state["button_clicked"] = "What are key actions we can take to improve reliability in our network"
            if st.button("Are there any regions or departments experiencing notable deviations or issues?"):
                st.session_state["button_clicked"] = "Are there any regions or departments experiencing notable deviations or issues?"

if st.session_state["button_clicked"]:
    sendMessage(st.session_state["button_clicked"])
    st.session_state["button_clicked"] = None

# User input
if prompt := st.chat_input("Type your message..."):
    sendMessage(prompt)




    





