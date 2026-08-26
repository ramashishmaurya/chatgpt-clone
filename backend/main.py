from fastapi import FastAPI

from routes.upload import router as upload_router


app = FastAPI()


app.include_router(upload_router)


@app.get("/")
def root():
    return {
        "message": "API is running"
    }