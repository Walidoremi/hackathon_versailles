from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import health, chat, multi_chat, ui
from .middleware.request_id import RequestIDMiddleware
import pandas as pd

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="LLM Chat API",
    version="0.1.0",
    description="Squelette d'API FastAPI pour brancher un chatbot (ex: Mistral)",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(multi_chat.router, prefix="/api/v1", tags=["multi-agents"])
app.include_router(ui.router, tags=["ui"])

@app.get("/api/", include_in_schema=False)
async def api_root():
    return {
        "name": "LLM Chat API",
        "version": "0.1.0",
        "docs": "/api/docs",
        "health": "/api/v1/health",
    }
