from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.upload import router as upload_router
from routes.chat import router as ask_question
from database import engine
import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware to allow the frontend (Vite) to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, you can restrict this to ["http://localhost:5173"] in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(upload_router)
app.include_router(ask_question)


@app.get("/")
def root():
    return {
        "message": "API is running"
    }


@app.get("/username")
def username():
    return{
        'name' : 'nam is ashish okay '
    } 