from fastapi import FastAPI

from app.database import Base, engine
from app import models  # noqa: F401
from app.routers import trips

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Visa Rule Watchdog")

app.include_router(trips.router)


@app.get("/health")
def health():
    return {"status": "ok"}