"""
API routers module exports.
"""

from routers.health import router as health_router
from routers.predictions import router as predictions_router
from routers.metadata import router as metadata_router
from routers.patients import router as patients_router
from routers.fso import router as fso_router

__all__ = [
    "health_router",
    "predictions_router",
    "metadata_router",
    "patients_router",
    "fso_router",
]
