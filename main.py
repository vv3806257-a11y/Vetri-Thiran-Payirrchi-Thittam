from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from backend.routes import router

load_dotenv()

app = FastAPI(
    title="LegalEase API",
    description="AI-powered legal document draft generator.",
    version="1.0.0",
)

origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:8501,http://127.0.0.1:8501",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", tags=["health"])
def root():
    return {
        "status": "ok",
        "service": "LegalEase API",
        "version": "1.0.0",
    }


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}
