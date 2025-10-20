import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from powerbi_client import get_latest_metrics, get_data_from_dataset_with_query
from intent import classify_intent
from langchain_community.llms import OpenAI
from langchain_community.vectorstores import Pinecone as LC_Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from langchain.chains import RetrievalQA
from langchain_pinecone import Pinecone

load_dotenv()

pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENV")

pc = Pinecone(api_key=pinecone_api_key, environment=pinecone_env)

index_name = "psa-vectorstore"
index = pc.Index(index_name)

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embeddings = HuggingFaceEmbeddings(model=model)

vectorstore = LC_Pinecone(index, embeddings)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2025-01-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT")
)

retriever = vectorstore.as_retriever()

qa_chain = RetrievalQA.from_chain_type(
    client,
    retriever=retriever,
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

def query_dashboard(history: list, query: str, data: str) -> str: 
    try:
        prompt = f"""
        You are an AI Assistant that answers user's queries about PSA's global insights dashboard.
        Here is the relevant information extracted from the dashboard:\n
        {data}
        Given the following query, answer the user's query, focusing on PSA's global strategy of operational synergy,
        real-time visibility and sustainability across the supply chain.        
        """

        messages = [{"role": "system", "content": prompt}] + history +  [
            {"role": "user", "content": query}
        ]
            
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=messages,
            max_tokens=50
        )
        output = response.choices[0].message.content
        return output
    except Exception as e:
        print(f"Error converting query to DAX: {e}")
        return None

def chat_with_dashboard(history: list, message: str) -> str:
    intent = classify_intent(message)
    print(intent)

    if "summary" == intent:
        summary = summarize_metrics(get_latest_metrics())
        return f"Here’s the current dashboard summary:\n\n{summary}"
    
    elif "query" == intent: 
        dax_query = query_to_dax(message)
        data = get_data_from_dataset_with_query(dax_query)
        return query_dashboard(history, message, data)

    relevant_chunks = similarity_search(message)

    context = "\n".join(relevant_chunks)
    prompt = f"""
    You are an AI assistant helping PSA interpret its Global Insights Dashboard.

    Respond to the user’s questions based on current operational metrics,
    focusing on real-time visibility, synergy, and sustainability.

    Additional context: 
    {context}
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


def query_to_dax(query):
    try:
        prompt = f"""
        You are an expert in Power BI DAX queries.
        Given the following query, return only the DAX expression needed to answer it. 
        Do not provide any explanations or extra text. Just return the DAX expression.        
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

def similarity_search(query: str, top_k: int = 5):
    query_embedding = embeddings.embed_query(query)
    result = index.query(
        vector=query_embedding,
        top_k=top_k,
    )

    if not result['matches']:
        return []

    relevant_chunks = [match['metadata']['text'] for match in result['matches']]
    return relevant_chunks