from fastapi import FastAPI
from pydantic import BaseModel
from rag_test import ask

app = FastAPI()

class AskRequest(BaseModel):
    question: str

@app.post("/ask")

def ask_endpoint(request: AskRequest):
    answer = ask(request.question)
    return {"answer": answer}