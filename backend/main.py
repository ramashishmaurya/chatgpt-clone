from fastapi import FastAPI

from routes.upload import router as upload_router
from routes.chat import router as ask_question


app = FastAPI()


app.include_router(upload_router)
app.include_router(ask_question)


@app.get("/")
def root():
    return {
        "message": "API is running"
    }