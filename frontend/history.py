import sqlite3
import json
import uuid
import os

DB_FILE = "chat_history.db"


# Initialize SQLite DB and table
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    user_id TEXT PRIMARY KEY,
    messages TEXT
)
""")
conn.commit()


def get_user_id(session_state):
    """Generate or retrieve a unique user ID for this Streamlit session."""
    if "user_id" not in session_state:
        session_state["user_id"] = str(uuid.uuid4())
    return session_state["user_id"]


def load_history(user_id):
    """Load chat history from SQLite."""
    c.execute("SELECT messages FROM chat_history WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row:
        return json.loads(row[0])
    return []


def save_history(user_id, messages):
    """Save chat history to SQLite."""
    data = json.dumps(messages)
    c.execute("REPLACE INTO chat_history (user_id, messages) VALUES (?, ?)", (user_id, data))
    conn.commit()


def clear_history(user_id):
    """Delete the user's chat history from SQLite."""
    c.execute("DELETE FROM chat_history WHERE user_id=?", (user_id,))
    conn.commit()