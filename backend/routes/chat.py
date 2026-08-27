from fastapi import APIRouter
from pydantic import BaseModel

from rag_services import ask_question


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
):

    answer = await ask_question(
        session_id=request.session_id,
        question=request.question,
    )

    return {
        "question": request.question,
        "answer": answer,
    }