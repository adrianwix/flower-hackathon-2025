"""
Database configuration and connection management.
"""

import os
from typing import Generator

from sqlmodel import SQLModel, Session, create_engine, select


# Database URL from environment variable or default to local PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/radiology_review",
)

# Create engine
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """Create all tables in the database"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency to get a database session.
    Use this in FastAPI endpoints with Depends(get_session)
    """
    with Session(engine) as session:
        yield session


def init_pathologies(session: Session) -> None:
    """
    Initialize pathology codes based on NIH Chest X-ray dataset.
    Should be called once during database initialization.
    """
    from models import Pathology

    pathologies = [
        {
            "code": "NO_FINDING",
            "display_name": "No Finding",
            "description": "No pathology detected in the X-ray",
        },
        {
            "code": "ANY_PATHOLOGY",
            "display_name": "Any Pathology",
            "description": "One or more pathologies detected",
        },
        # NIH Chest X-ray dataset pathologies
        {
            "code": "ATELECTASIS",
            "display_name": "Atelectasis",
            "description": "Collapse or incomplete inflation of the lung",
        },
        {
            "code": "CARDIOMEGALY",
            "display_name": "Cardiomegaly",
            "description": "Enlargement of the heart",
        },
        {
            "code": "EFFUSION",
            "display_name": "Effusion",
            "description": "Abnormal fluid accumulation in pleural space",
        },
        {
            "code": "INFILTRATION",
            "display_name": "Infiltration",
            "description": "Presence of substances denser than air in lung parenchyma",
        },
        {
            "code": "MASS",
            "display_name": "Mass",
            "description": "Space-occupying lesion larger than 3 cm",
        },
        {
            "code": "NODULE",
            "display_name": "Nodule",
            "description": "Space-occupying lesion less than 3 cm",
        },
        {
            "code": "PNEUMONIA",
            "display_name": "Pneumonia",
            "description": "Infection of the lung",
        },
        {
            "code": "PNEUMOTHORAX",
            "display_name": "Pneumothorax",
            "description": "Presence of air in the pleural space",
        },
        {
            "code": "CONSOLIDATION",
            "display_name": "Consolidation",
            "description": "Region of normally compressible lung tissue filled with liquid",
        },
        {
            "code": "EDEMA",
            "display_name": "Edema",
            "description": "Fluid accumulation in the lungs",
        },
        {
            "code": "EMPHYSEMA",
            "display_name": "Emphysema",
            "description": "Enlargement of air spaces in the lungs",
        },
        {
            "code": "FIBROSIS",
            "display_name": "Fibrosis",
            "description": "Thickening and scarring of connective tissue",
        },
        {
            "code": "PLEURAL_THICKENING",
            "display_name": "Pleural Thickening",
            "description": "Thickening of the pleura",
        },
        {
            "code": "HERNIA",
            "display_name": "Hernia",
            "description": "Abnormal protrusion of tissue",
        },
    ]

    for path_data in pathologies:
        # Check if pathology already exists
        existing = session.exec(
            select(Pathology).where(Pathology.code == path_data["code"])
        ).first()
        if not existing:
            pathology = Pathology(
                code=path_data["code"],
                display_name=path_data["display_name"],
                description=path_data["description"],
            )
            session.add(pathology)

    session.commit()
