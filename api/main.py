"""
Flower Hackathon API - Radiology Review System

Main application entry point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from config import API_TITLE, API_DESCRIPTION, API_VERSION, CORS_ORIGINS
from database import create_db_and_tables, init_pathologies, engine
from routers import (
    health_router,
    predictions_router,
    metadata_router,
    patients_router,
    fso_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Create tables and initialize data
    create_db_and_tables()

    # Initialize pathologies if needed
    with Session(engine) as session:
        init_pathologies(session)

    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)
app.include_router(predictions_router)
app.include_router(metadata_router)
app.include_router(patients_router)
app.include_router(fso_router)
