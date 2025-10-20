import os
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import numpy as np
import pinecone
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENV")

pc = Pinecone(api_key=pinecone_api_key)

index_name = "psa-vectorstore" 
if index_name not in [idx.name for idx in pc.list_indexes()]: 
    pc.create_index( name=index_name, dimension=384,
                    metric="cosine", spec=ServerlessSpec(cloud="aws", region="us-east-1") ) 
    print(f"Pinecone index '{index_name}' ready!")

with open("psa.txt", "r", encoding="utf-8") as f:
    text = f.read()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_text(text)

documents = [Document(page_content=chunk, metadata={"title": "PSA Info", "source": "psa.txt"}) for chunk in chunks]

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

embeddings = model.encode([doc.page_content for doc in documents], convert_to_numpy=True)

index = pc.Index(index_name)

upsert_data = [
    {"id": str(i), "values": embeddings[i].tolist(), "metadata": documents[i].metadata}
    for i in range(len(documents))
]

index.upsert(vectors=upsert_data)
print("Documents successfully pushed to Pinecone!")
