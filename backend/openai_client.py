import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_metrics(metrics: dict) -> str:
    prompt = f"""
    You are PSA InsightCopilot, an AI assistant that interprets Power BI metrics.
    Metrics: {metrics}
    Write a concise business summary and suggest next actions aligned with PSA's global strategy.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content