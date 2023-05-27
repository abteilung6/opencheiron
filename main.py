from core.lifespan import LifespanManager
from fastapi import FastAPI
from core.config import settings
from api.api import api_router


app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
def startup_event():
    LifespanManager.startup()
