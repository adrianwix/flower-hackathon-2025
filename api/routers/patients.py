"""
Patient management endpoints.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from sqlmodel import Session, select

from dependencies import get_session
from services import PatientService
from models import Image


class DoctorLabelUpdate(BaseModel):
    labels: Dict[str, bool]
    comment: Optional[str] = None


router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("")
async def list_patients(
    session: Session = Depends(get_session),
) -> List[Dict[str, Any]]:
    """
    List all patients with review status.

    Returns:
        List of patients with:
        - Patient details (name, age, gender)
        - Review status (needs review / reviewed)
        - Last follow-up date
    """
    patient_service = PatientService(session)
    return await patient_service.list_patients_with_status()


@router.get("/{patient_id}")
async def get_patient_details(
    patient_id: int,
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    """
    Get patient details with all exams and images.

    Args:
        patient_id: Patient ID

    Returns:
        Patient details including:
        - Personal information
        - All exams with images
        - ML and doctor labels for each image
    """
    patient_service = PatientService(session)
    return await patient_service.get_patient_with_exams(patient_id)


@router.post("/{patient_id}/exams")
async def create_exam_with_image(
    patient_id: int,
    file: UploadFile = File(...),
    exam_datetime: str = Form(None),
    reason: str = Form(None),
    view_position: str = Form(None),
    threshold: float = Form(0.5),
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    """
    Upload a new exam with X-ray image for a patient.

    This endpoint:
    1. Creates a new exam
    2. Uploads and stores the image
    3. Runs ML inference on the image
    4. Returns the exam with predictions

    Args:
        patient_id: Patient ID
        file: X-ray image file
        exam_datetime: Exam datetime (ISO format, optional)
        reason: Reason for exam (optional)
        view_position: X-ray view position (e.g., "PA", "AP")
        threshold: Probability threshold for predictions

    Returns:
        Created exam with image and ML predictions
    """
    # Parse exam datetime if provided
    parsed_datetime = None
    if exam_datetime:
        try:
            parsed_datetime = datetime.fromisoformat(
                exam_datetime.replace("Z", "+00:00")
            )
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid exam_datetime format. Use ISO format."
            )

    # Read image bytes
    image_bytes = await file.read()

    # Create exam and run inference
    patient_service = PatientService(session)
    result = await patient_service.create_exam_with_image(
        patient_id=patient_id,
        image_bytes=image_bytes,
        filename=file.filename or "unknown.png",
        exam_datetime=parsed_datetime,
        reason=reason,
        view_position=view_position,
        threshold=threshold,
    )

    return result


@router.get("/images/{image_id}")
async def get_image(
    image_id: int,
    session: Session = Depends(get_session),
) -> Response:
    """
    Get the actual image bytes for an X-ray image.

    Args:
        image_id: Image ID

    Returns:
        Image bytes with appropriate content type
    """
    statement = select(Image).where(Image.id == image_id)
    image = session.exec(statement).first()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    return Response(
        content=image.image_bytes,
        media_type=image.mime_type,
        headers={
            "Content-Disposition": f'inline; filename="{image.filename}"',
        },
    )


@router.put("/images/{image_id}/labels")
async def update_doctor_labels(
    image_id: int,
    update: DoctorLabelUpdate,
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    """
    Update doctor labels for an image.

    This endpoint allows doctors to:
    - Confirm ML predictions
    - Override ML predictions
    - Add comments

    Args:
        image_id: Image ID
        labels: Dictionary of pathology codes to boolean values
                e.g., {"Cardiomegaly": true, "Effusion": false}
        comment: Optional comment from doctor

    Returns:
        Updated doctor labels
    """
    patient_service = PatientService(session)
    return await patient_service.update_doctor_labels(
        image_id=image_id,
        labels=update.labels,
        comment=update.comment,
    )
