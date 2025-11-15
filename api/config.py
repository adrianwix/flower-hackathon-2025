"""
Application configuration.
"""

import os

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/postgres",
)

# API
API_TITLE = "Flower Hackathon API - Radiology Review System"
API_DESCRIPTION = (
    "API for managing patient X-ray records and AI-assisted pathology detection"
)
API_VERSION = "0.1.0"

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Model
DEFAULT_MODEL_VERSION = "mock_v1"
DEFAULT_PREDICTION_THRESHOLD = 0.5
