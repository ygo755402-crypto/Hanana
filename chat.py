from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import create_database, import_file, all_text
from brain import Brain

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_database()
documents = all_text()
if not documents:
    import_file()
    documents = all_text()

brain = Brain(documents)

history = []

class ChatQuery(BaseModel):
    question: str

@app.post("/chat")
async def chat_endpoint(data: ChatQuery):
    global history
    question = data.question.strip()
    
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    search_question = question
    if history and len(question.split()) <= 4:
        search_question = history[-1] + " " + question

    answer, confidence, results = brain.answer(search_question)

    if answer is None or confidence < 0.20:
        return {
            "answer": "I don't have the information ",
            "match": 0.0
        }

    history.append(question)
    if len(history) > 5:
        history.pop(0)

    return {
        "answer": answer,
        "match": round(confidence * 100, 1)
    }
