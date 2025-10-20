FROM python:3.11-bookworm

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt

RUN pip install --no-cache-dir -r backend/requirements.txt
RUN pip install --no-cache-dir streamlit

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "frontend/main.py", "--server.enableCORS", "false", "--server.enableXsrfProtection", "false"]
