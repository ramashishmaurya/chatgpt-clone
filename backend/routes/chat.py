from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from rag_services import ask_question, stream_question
from database import get_db
from models import ChatSession, ChatMessage


router = APIRouter(
    prefix="/api",
    tags=["Chat"],
)


class ChatRequest(BaseModel): # here using the pydanric for validation okay 
    session_id: str
    question: str


@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    
    # Check if session exists, if not create it
    db_session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
    if not db_session:
        db_session = ChatSession(
            id=request.session_id, 
            title=request.question[:25] + "..." if request.question else "New Chat"
        )
        db.add(db_session)
        db.commit()

    # Save user message
    user_msg = ChatMessage(session_id=request.session_id, role="user", content=request.question)
    db.add(user_msg)
    db.commit()

    # Get answer from RAG / LLM
    answer = await ask_question(
        session_id=request.session_id,
        question=request.question,
    )
    
    # Save bot message
    bot_msg = ChatMessage(session_id=request.session_id, role="bot", content=answer)
    db.add(bot_msg)
    db.commit()

    return {
        "question": request.question,
        "answer": answer,
    }

@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    
    # Check if session exists, if not create it
    db_session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
    if not db_session:
        db_session = ChatSession(
            id=request.session_id, 
            title=request.question[:25] + "..." if request.question else "New Chat"
        )
        db.add(db_session)
        db.commit()

    # Save user message
    user_msg = ChatMessage(session_id=request.session_id, role="user", content=request.question)
    db.add(user_msg)
    db.commit()

    async def event_generator():
        full_answer = ""
        async for chunk in stream_question(
            session_id=request.session_id,
            question=request.question,
        ):
            yield chunk
            full_answer += chunk
        
        # Save bot message
        bot_msg = ChatMessage(session_id=request.session_id, role="bot", content=full_answer)
        db.add(bot_msg)
        db.commit()

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/chats")
def get_chats(db: Session = Depends(get_db)):
    chats = db.query(ChatSession).order_by(ChatSession.created_at.desc()).all()
    return [
        {
            "id": c.id,
            "title": c.title
        } for c in chats
    ]

@router.get("/chat/{session_id}/messages")
def get_chat_messages(session_id: str, db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
    return [
        {
            "id": str(m.id),
            "role": m.role,
            "content": m.content
        } for m in messages
    ]

@router.post("/chat/new")
def create_new_chat(db: Session = Depends(get_db)):
    new_id = str(uuid.uuid4())
    db_session = ChatSession(id=new_id, title="New Chat")
    db.add(db_session)
    db.commit()
    return {"id": new_id, "title": "New Chat"}


@router.delete("/chat/{session_id}")
def delete_chat_session(session_id: str, db: Session = Depends(get_db)):
    db_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    db.delete(db_session)
    db.commit()
    return {"message": "Chat deleted successfully"}


