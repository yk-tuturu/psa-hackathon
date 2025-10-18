import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from powerbi_client import get_latest_metrics

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2025-01-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT")
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
        model=os.getenv("OPENAI_MODEL"),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )

    return response.choices[0].message.content


def chat_with_dashboard(history: list, message: str) -> str:
    prompt = f"""
    Classify the intent of the following user message.
    Return one of: [summary, other]

    Message: "{message}"
    """

    response = client.chat.completions.create(
        model=os.getenv("GPT4_MODEL"),
        messages=[{"role": "user", "content": prompt}]
    )

    intent = response.choices[0].message.content.strip().lower()
    print(intent)

    
    prompt = f"""
    You are an AI assistant helping PSA interpret its Global Insights Dashboard.

    Respond to the user’s questions based on current operational metrics,
    focusing on real-time visibility, synergy, and sustainability.
    """

    if "summary" == intent:
        summary = summarize_metrics(get_latest_metrics())
        return f"Here’s the current dashboard summary:\n\n{summary}"

    

    messages = [{"role": "system", "content": prompt}] + history + [
        {"role": "user", "content": message}
    ]



    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        messages=messages,
        max_tokens=500
    )

    return response.choices[0].message.content

#if __name__ == "__main__":
#    sample_metrics = {
#        "berth_time": 12.5,
#        "carbon_savings": 1500,
#        "arrival_accuracy": 95.2
#    }
#    summary = summarize_metrics(sample_metrics)
#    print(summary)
