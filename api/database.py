"""
Database configuration and connection management.
"""

from sqlmodel import SQLModel, Session, create_engine, select

from config import DATABASE_URL
from constants import PATHOLOGY_CODES, PATHOLOGY_METADATA


# Create engine
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """Create all tables in the database"""
    SQLModel.metadata.create_all(engine)


def init_pathologies(session: Session) -> None:
    """
    Initialize pathology codes matching torchxrayvision model outputs.
    Uses centralized PATHOLOGY_CODES from constants.py
    Also includes binary classification label (Finding)
    """
    from models import Pathology

    # Multi-label pathologies from torchxrayvision
    pathologies = [
        {
            "code": code,
            "display_name": PATHOLOGY_METADATA[code]["display_name"],
            "description": PATHOLOGY_METADATA[code]["description"],
        }
        for code in PATHOLOGY_CODES
    ]

    # Add binary classification label
    pathologies.append(
        {
            "code": "Finding",
            "display_name": PATHOLOGY_METADATA["Finding"]["display_name"],
            "description": PATHOLOGY_METADATA["Finding"]["description"],
        }
    )

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
