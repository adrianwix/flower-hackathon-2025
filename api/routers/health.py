"""
Health check and root endpoints.
"""

from fastapi import APIRouter

from config import API_TITLE, API_VERSION

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": API_TITLE,
        "version": API_VERSION,
    }
