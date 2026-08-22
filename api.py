from fastapi import FastAPI
from pydantic import BaseModel
import anthropic

app = FastAPI()
client = anthropic.Anthropic()

class TranslateRequest(BaseModel):
    text: str

@app.post("/translate")
def translate(request: TranslateRequest):
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        temperature=0,
        system="你是翻译器，把用户输入翻译成德语，只输出译文，不要任何解释",
        messages=[{"role": "user", "content": request.text}]
    )
    reply = next(b.text for b in response.content if b.type == "text")
    return {"translation": reply}