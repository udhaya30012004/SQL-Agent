"""
Agentic Data Analyst — FastAPI Application Entry Point

Configures the application, middleware, static file serving,
and registers all routers (auth, chat, sql, pandas).
"""

import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Add project root to sys.path so we can import from shared, SQL_Agent, etc.
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.app.core.config import settings
from api.app.db.session import engine, Base

# Import ALL models so SQLAlchemy knows about them at table-creation time
from api.app.models.user import User          # noqa: F401
from api.app.models.chat import ChatSession, ChatMessage  # noqa: F401

from api.app.routers import auth, chat, sql_agent, pandas_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown actions.
    Automatically creates PostgreSQL metadata tables for users, chat sessions,
    and messages if they do not exist.
    """
    # Create all metadata tables (users + chat_sessions + chat_messages)
    Base.metadata.create_all(bind=engine)

    # Ensure charts output directory exists
    os.makedirs(settings.CHARTS_DIR, exist_ok=True)

    print(f"OK {settings.PROJECT_NAME} started successfully")
    print("API docs: http://localhost:8000/docs")

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS middleware
# Use explicitly listed origins in production; fall back to wildcard for dev
cors_origins = (
    [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
    if settings.BACKEND_CORS_ORIGINS
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount charts directory to serve generated Plotly HTML files statically
# e.g., http://localhost:8000/charts/bar_chart.html
app.mount(
    "/charts",
    StaticFiles(directory=settings.CHARTS_DIR),
    name="charts",
)

# ==========================================
# REGISTER ROUTERS
# ==========================================
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(sql_agent.router, prefix=settings.API_V1_STR)
app.include_router(pandas_agent.router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME}!",
        "documentation": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
