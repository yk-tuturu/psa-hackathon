# Navi-bot

A smart assistant for interpreting dashboard analytics and providing actionable insights. Allows for faster monitoring of globally connected networks and improves operation synergy.

View it live here -> https://psa-hackathon.streamlit.app/

## Features
UI
- Seamless and modern chatbot interface for easy querying
- Embedded Microsoft BI dashboard to reference
- Lightweight sqlite database for storing chat history

Backend
- FastAPI: automatic API generation, data validation, and asynchronous capabilities for backend
- LangChain + Pinecone vectorstore for retrieval augmented generation of relevant context and data, ensuring that the chatbot can generate accurate, informative responses.
- OpenAI LLM handles natural language as chatbot to respond to users.
- Power BI API to query data from dashboard, through DAX queries to apply filters


## Screenshots
<p float="left">
  <img src="https://i.imgur.com/I6KKVXD.png" alt="Screenshot of gameplay" width=600/>
  
</p>
<img src="https://i.imgur.com/zY8L0yy.png" alt="Screenshot of gameplay" width=600/>

### Setup to run locally
1. Clone the repo onto your machine
2. (Recommended) Start a python venv in the root folder
```
python -m venv venv
```
3. Install all dependencies
```
pip install requirements.txt
```
4. Navigate to the frontend folder and create an .env file with the following fields
```
COOKIE_PASSWORD=<Any random string, will be used as a password for the cookies>
BACKEND_URL=<Your backend url>
```
5. Start the Streamlit app
```
streamlit run main.py
```
5. In another terminal, navigate to the backend folder.
```
cd backend
```
6. Create a .env file with the following fields:
```
POWERBI_TENANT_ID=?
POWERBI_WORKSPACE_ID=?
POWERBI_REPORT_ID=?
OPENROUTER_API_KEY=?
AZURE_OPENAI_API_KEY=?
AZURE_OPENAI_API_ENDPOINT=https://psacodesprint2025.azure-api.net/
OPENAI_MODEL=gpt-4.1-nano
GPT4_MODEL=gpt-4.1-mini
POWERBI_CLIENT_ID=?
POWERBI_CLIENT_SECRET=?
```
8. Start the backend server
```
uvicorn main:app --reload
```




