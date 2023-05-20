from fastapi import FastAPI
from core.config import settings


app = FastAPI(title=settings.PROJECT_NAME)


@app.get("/")
async def root():
    return {"message": "Hello World"}
