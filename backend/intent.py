import numpy as np
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2025-01-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT")
)

# Predefined intents with example text
intent_examples = {
    "summary": [
        "Provide a summary of the dashboard metrics",
        "Give me an overview of the dashboard",
        "Big picture view of what is going on"
    ],
    "question": [
        "Ask a specific question about the metrics or performance",
        "What was the increase in carbon emission over the past 2 years?"
        "Which metrics showed the greatest increase over the past 2 months?"
    ],
    "action": [
        "Request an action or next steps based on metrics",
        "Provide me with actionables based on our current metrics to improve our performance"
    ],
    "other": "Anything that does not fit the above categories"
}

# Precompute embeddings for intents
intent_embeddings = {}
for intent, text in intent_examples.items():
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    intent_embeddings[intent] = response.data[0].embedding

# Cosine similarity function
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def classify_intent(user_message: str) -> str:
    """Return the predicted intent based on embedding similarity."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=user_message
    )
    user_embedding = response.data[0].embedding
    similarities = {intent: cosine_similarity(user_embedding, emb)
                    for intent, emb in intent_embeddings.items()}
    return max(similarities, key=similarities.get)
