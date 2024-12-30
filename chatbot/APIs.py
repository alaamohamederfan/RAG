from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.schema import HumanMessage, AIMessage
from RAG import qa_chain
app = FastAPI()
chat_history = []

# Pydantic models for API
class QueryRequest(BaseModel):
    Query: str

class QueryResponse(BaseModel):
    answer: str

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    try:

        Query = request.Query
        response = qa_chain({"question": Query, "chat_history": chat_history})

        chat_history.extend([
            HumanMessage(content=Query),
            AIMessage(content=response["answer"]),
        ])
        print(response["answer"])
        return QueryResponse(answer=response["answer"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
async def reset_chat():
    """Endpoint to reset chat history."""
    global chat_history
    chat_history = []
    return {"message": "Chat history has been reset."}

@app.get("/history")
async def get_chat_history():
    """Endpoint to fetch the current chat history."""
    return {"chat_history": [message.content for message in chat_history]}
