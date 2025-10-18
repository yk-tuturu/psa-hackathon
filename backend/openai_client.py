import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def summarize_metrics(metrics: dict) -> str:
    prompt = f"""
    You are an AI assistant that interprets key operational metrics 
    from PSA’s Global Insights Dashboard.

    Your goal is to:
    1. Summarise the provided metrics in clear, professional business language.
    2. Highlight notable trends, improvements, or anomalies (e.g., changes in berth time, carbon savings, or arrival accuracy).
    3. Suggest 2–3 actionable next steps aligned with PSA’s global strategy of 
    operational synergy, real-time visibility, and sustainability across the supply chain.

    Metrics data:
    {metrics}

    Write your response in this format:
    **Summary:** <1–2 sentence business overview>
    **Key Observations:** <bullet points on performance or issues>
    **Recommended Actions:** <bullet points suggesting next steps>

    Be concise, insightful, and use data-driven reasoning suitable for a management dashboard.
    """

    response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    sample_metrics = {
        "berth_time": 12.5,
        "carbon_savings": 1500,
        "arrival_accuracy": 95.2
    }
    summary = summarize_metrics(sample_metrics)
    print(summary)
