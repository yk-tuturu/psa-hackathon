import requests
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")

def get_chat_completion(prompt, history):
    payload = {
        "history": history,  # entire conversation so far
        "message": prompt     # new user message
    }

    try:
        res = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
        if res.status_code == 200:
            return res.json().get("reply", "No reply received")
        else:
            return f"Error {res.status_code}: {res.text}"
    except Exception as e:
        return f"Error: {e}"