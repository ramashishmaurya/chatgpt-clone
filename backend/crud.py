from sqlalchemy.orm import Session
from models import ChatSession, ChatMessage
import uuid

# --- Chat Session CRUD ---

def get_session(db: Session, session_id: str):
    return db.query(ChatSession).filter(ChatSession.id == session_id).first()

def get_sessions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ChatSession).offset(skip).limit(limit).all()

def create_session(db: Session, session_id: str = None, title: str = "New Chat"):
    # If no session_id is provided, generate a new UUID
    if not session_id:
        session_id = str(uuid.uuid4())
        
    db_session = ChatSession(id=session_id, title=title)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_session_title(db: Session, session_id: str, new_title: str):
    db_session = get_session(db, session_id)
    if db_session:
        db_session.title = new_title
        db.commit()
        db.refresh(db_session)
    return db_session

def delete_session(db: Session, session_id: str):
    db_session = get_session(db, session_id)
    if db_session:
        db.delete(db_session)
        db.commit()
        return True
    return False

# --- Chat Message CRUD ---

def get_messages_for_session(db: Session, session_id: str):
    return db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()

def create_chat_message(db: Session, session_id: str, role: str, content: str):
    db_message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
