"""
Metadata endpoints for pathologies and model versions.
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from dependencies import get_session
from models import ModelVersion, Pathology

router = APIRouter(tags=["metadata"])


@router.get("/pathologies")
async def list_pathologies(session: Session = Depends(get_session)):
    """
    List all available pathology codes.

    Returns:
        List of all pathologies in the system
    """
    pathologies = session.exec(select(Pathology)).all()
    return {"pathologies": pathologies}


@router.get("/model-versions")
async def list_model_versions(session: Session = Depends(get_session)):
    """
    List all available model versions.

    Returns:
        List of all model versions in the system
    """
    versions = session.exec(select(ModelVersion)).all()
    return {"model_versions": versions}
