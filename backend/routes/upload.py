from fastapi import APIRouter, UploadFile, File, HTTPException , Form, Depends
from sqlalchemy.orm import Session
from upload_data import load_and_split
from vector_store import add_documents
import uuid
from database import get_db
from models import ChatSession

router = APIRouter(
    prefix="/api",
    tags=["Upload"]
)


@router.post("/upload")
async def upload_file(
    # session_id: str = Form(...) ,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Validate file
        if not file.filename: 
            raise HTTPException(
                status_code=400,
                detail="File name is required"
            )

        allowed_extensions = {
            ".pdf",
            ".docx",
            ".txt"
        }

        extension = "." + file.filename.split(".")[-1].lower()

        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Only PDF, DOCX and TXT files are supported"
            )

        # Read uploaded file
        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        # Load + split document
        documents = load_and_split(
            file_bytes=file_bytes,
            filename=file.filename
        )

        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No content found in the file"
            )

        session_id = str(uuid.uuid4())
        # Store chunks in Qdrant
        vectorstore = add_documents(
            session_id=session_id,
            documents=documents
        )
        
        # Save session to DB
        title = file.filename
        if len(title) > 25:
            title = title[:25] + "..."
        db_session = ChatSession(id=session_id, title=title)
        db.add(db_session)
        db.commit()

        return {
            "success": True,
            "message": "File uploaded and stored in Qdrant successfully",
            "session_id": session_id,
            "filename": file.filename,
            "chunks": len(documents),
            "collection": session_id
        }

    except HTTPException:
        raise

    except Exception as e:
        print(f"Upload error: {e}")

        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {str(e)}"
        )
