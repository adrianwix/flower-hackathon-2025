"""
SQLModel models for the radiology review application.
Based on the PostgreSQL schema in DATA_MODEL.md
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List

from sqlmodel import (
    SQLModel,
    Field,  # type: ignore
    Relationship,
)


# =========================================================
# Enums
# =========================================================


class UserRole(str, Enum):
    """User roles in the system"""

    DOCTOR = "doctor"
    ADMIN = "admin"


# =========================================================
# User (Doctor)
# =========================================================


class User(SQLModel, table=True):
    """Users (doctors) table"""

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, nullable=False, index=True)
    full_name: str = Field(nullable=False)
    password_hash: str = Field(nullable=False)  # Can be dummy for hackathon
    role: str = Field(default=UserRole.DOCTOR.value, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    created_exams: List["Exam"] = Relationship(back_populates="creator")
    doctor_labels: List["DoctorLabel"] = Relationship(back_populates="labeled_by_user")


# =========================================================
# Patient
# =========================================================


class Patient(SQLModel, table=True):
    """Patients table"""

    id: Optional[int] = Field(default=None, primary_key=True)
    external_patient_id: Optional[str] = Field(
        default=None
    )  # e.g., NIH Patient ID for seeded data
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    birth_year: Optional[int] = Field(default=None)
    sex: Optional[str] = Field(default=None)  # 'M', 'F', 'O', etc.
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    exams: List["Exam"] = Relationship(back_populates="patient")


# =========================================================
# Exam
# =========================================================


class Exam(SQLModel, table=True):
    """Exams (visits / imaging sessions) table"""

    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patient.id", nullable=False, index=True)
    exam_datetime: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    reason: Optional[str] = Field(default=None)  # Free text
    created_by: Optional[int] = Field(default=None, foreign_key="user.id", index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    patient: Patient = Relationship(back_populates="exams")
    creator: Optional[User] = Relationship(back_populates="created_exams")
    images: List["Image"] = Relationship(back_populates="exam")


# =========================================================
# Image (X-ray)
# =========================================================


class Image(SQLModel, table=True):
    """Images (X-rays) table - stores image bytes and metadata"""

    id: Optional[int] = Field(default=None, primary_key=True)
    exam_id: int = Field(foreign_key="exam.id", nullable=False, index=True)

    # Raw image data
    filename: str = Field(nullable=False)
    image_bytes: bytes = Field(nullable=False)  # Actual X-ray bytes
    mime_type: str = Field(default="image/png", nullable=False)

    # Optional metadata
    view_position: Optional[str] = Field(default=None)  # e.g., "PA", "AP"

    # Workflow - image is pending review if reviewed_at is None
    reviewed_at: Optional[datetime] = Field(default=None, nullable=True, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    exam: Exam = Relationship(back_populates="images")
    predicted_labels: List["ImagePredictedLabel"] = Relationship(back_populates="image")
    doctor_labels: List["DoctorLabel"] = Relationship(back_populates="image")


# =========================================================
# Pathology
# =========================================================


class Pathology(SQLModel, table=True):
    """Pathology master table (binary or multi-label)"""

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, nullable=False, index=True)  # e.g., 'NO_FINDING'
    display_name: str = Field(nullable=False)  # e.g., "No Finding"
    description: Optional[str] = Field(default=None)

    # Relationships
    predicted_labels: List["ImagePredictedLabel"] = Relationship(
        back_populates="pathology"
    )
    doctor_labels: List["DoctorLabel"] = Relationship(back_populates="pathology")


# =========================================================
# Model Version
# =========================================================


class ModelVersion(SQLModel, table=True):
    """Model versions (FL rounds / weight snapshots)"""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)  # e.g., "fl_round_5_resnet34"
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    artifact_path: Optional[str] = Field(
        default=None
    )  # Path to weights on disk, if needed

    # Relationships
    predicted_labels: List["ImagePredictedLabel"] = Relationship(
        back_populates="model_version"
    )
    doctor_labels: List["DoctorLabel"] = Relationship(back_populates="model_version")


# =========================================================
# Image Predicted Label (ML output)
# =========================================================


class ImagePredictedLabel(SQLModel, table=True):
    """Image predicted labels (ML output)"""

    id: Optional[int] = Field(default=None, primary_key=True)
    image_id: int = Field(foreign_key="image.id", nullable=False, index=True)
    model_version_id: int = Field(
        foreign_key="modelversion.id", nullable=False, index=True
    )
    pathology_id: int = Field(foreign_key="pathology.id", nullable=False, index=True)

    probability: float = Field(nullable=False)  # Model's probability
    predicted_label: bool = Field(nullable=False)  # Thresholded yes/no

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    image: Image = Relationship(back_populates="predicted_labels")
    model_version: ModelVersion = Relationship(back_populates="predicted_labels")
    pathology: Pathology = Relationship(back_populates="predicted_labels")


# =========================================================
# Doctor Label (human validation/override of ML)
# =========================================================


class DoctorLabel(SQLModel, table=True):
    """Doctor labels (human validation / override of ML)"""

    id: Optional[int] = Field(default=None, primary_key=True)
    image_id: int = Field(foreign_key="image.id", nullable=False, index=True)
    model_version_id: int = Field(
        foreign_key="modelversion.id", nullable=False, index=True
    )
    pathology_id: int = Field(foreign_key="pathology.id", nullable=False, index=True)

    is_present: bool = Field(nullable=False)  # Doctor's decision for this pathology
    comment: Optional[str] = Field(default=None)

    labeled_by: int = Field(foreign_key="user.id", nullable=False, index=True)
    labeled_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    image: Image = Relationship(back_populates="doctor_labels")
    model_version: ModelVersion = Relationship(back_populates="doctor_labels")
    pathology: Pathology = Relationship(back_populates="doctor_labels")
    labeled_by_user: User = Relationship(back_populates="doctor_labels")
