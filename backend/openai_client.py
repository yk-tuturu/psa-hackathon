import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from powerbi_client import get_latest_metrics
from intent import classify_intent

load_dotenv()

# client = AzureOpenAI(
#     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#     api_version="2025-01-01-preview",
#     azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT")
# )

def make_client(apiKey: str):
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2025-01-01-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT")
    )

    return client

def summarize_metrics(metrics: dict, apiKey: str) -> str:
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
    client = make_client(apiKey)
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )

    return response.choices[0].message.content


def chat_with_dashboard(history: list, message: str, apiKey: str) -> str:
    intent = classify_intent(message, apiKey)
    print(intent)

    client = make_client(apiKey)

    if "summary" == intent:
        summary = summarize_metrics(get_latest_metrics(), apiKey)
        return f"Here’s the current dashboard summary:\n\n{summary}"

    
    prompt = f"""
    You are an AI assistant helping PSA interpret its Global Insights Dashboard.

    Respond to the user’s questions based on current operational metrics,
    focusing on real-time visibility, synergy, and sustainability.
    """

    messages = [{"role": "system", "content": prompt}] + history + [
        {"role": "user", "content": message}
    ]


    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        messages=messages,
        max_tokens=500
    )

    return response.choices[0].message.content


def query_to_dax(query: str, apiKey: str):
    client = make_client(apiKey)

    try:
        prompt = f"""
        You are an expert in Power BI DAX queries.
        Given the following query, return only the DAX expression needed to answer it. 
        Do not provide any explanations or extra text. Just return the DAX expression.

         The dataset for this report includes the following tables and fields:
        
        """

        messages = [{"role": "system", "content": prompt}] +  [
            {"role": "user", "content": query}
        ]
            
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=messages,
            max_tokens=50
        )
        dax_query = response.choices[0].message.content
        return dax_query
    except Exception as e:
        print(f"Error converting query to DAX: {e}")
        return None
