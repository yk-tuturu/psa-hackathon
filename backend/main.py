from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai_client import summarize_metrics, chat_with_dashboard
from powerbi_client import generate_embed_token, get_latest_metrics, get_report_details

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MetricsRequest(BaseModel):
    metrics: dict

class ChatMessage(BaseModel):
    history: list  # stateful, e.g. [{"role": "user", "content": ...}, {"role": "assistant", "content": ...}]
    message: str

@app.get("/report")
def get_report():
    return get_report_details()

@app.get("/embed-token")
def get_embed_token():
    return generate_embed_token()

@app.post("/summarize")
def summarize(request: MetricsRequest):
    summary = summarize_metrics(request.metrics)
    return {"summary": summary}


@app.post("/chat")
def chat(msg: ChatMessage):
    # Fetch live metrics before responding
    metrics = get_latest_metrics()

    reply = chat_with_dashboard(msg.history, msg.message, metrics)
    return {"reply": reply}
