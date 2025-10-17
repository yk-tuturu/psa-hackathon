from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from powerbi_client import get_report_details
from openai_client import summarize_metrics

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

@app.get("/report")
def get_report():
    return get_report_details()

@app.post("/summarize")
def summarize(request: MetricsRequest):
    summary = summarize_metrics(request.metrics)
    return {"summary": summary}
