from fastapi import FastAPI

app = FastAPI(title="Visa Rule Watchdog")
from fastapi import FastAPI

app = FastAPI(title="Visa Rule Watchdog")


@app.get("/health")
def health():
    return {"status": "ok"}