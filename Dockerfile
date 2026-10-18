FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

COPY documents.py rag_test.py rag_api.py ./

RUN python rag_test.py

CMD ["uvicorn", "rag_api:app", "--host", "0.0.0.0", "--port", "8000"]
