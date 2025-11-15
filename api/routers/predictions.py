"""
Prediction endpoints for X-ray pathology detection.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session

from dependencies import get_session
from services import PredictionService
from ml.preprocessing import validate_image as ml_validate_image


router = APIRouter(prefix="/predict", tags=["predictions"])


@router.post("")
async def predict_xray(
    file: UploadFile = File(...),
    threshold: float = 0.5,
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    """
    Predict pathologies for an uploaded X-ray image.

    This endpoint:
    1. Validates the uploaded image
    2. Runs the ML model to predict pathologies
    3. Returns predictions without storing them in the database

    Args:
        file: X-ray image file (PNG, JPEG)
        threshold: Probability threshold for positive predictions (0.0-1.0)

    Returns:
        Prediction results including binary and multi-label predictions
    """
    # Read image bytes
    image_bytes = await file.read()

    # Validate image
    is_valid, error_message = ml_validate_image(image_bytes)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    # Run prediction
    prediction_service = PredictionService(session)
    predictions = await prediction_service.predict_upload(
        image_bytes, threshold=threshold
    )

    return {
        "filename": file.filename,
        "predictions": predictions,
    }


@router.post("/{image_id}")
async def predict_stored_image(
    image_id: int,
    threshold: float = 0.5,
    model_version_name: Optional[str] = None,
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    """
    Run prediction on a stored image and save results to database.

    This endpoint:
    1. Retrieves the image from the database
    2. Runs the ML model to predict pathologies
    3. Stores predictions in the database

    Args:
        image_id: ID of the image in the database
        threshold: Probability threshold for positive predictions (0.0-1.0)
        model_version_name: Name of the model version (defaults to current mock model)

    Returns:
        Prediction results with database record IDs
    """
    prediction_service = PredictionService(session)
    return await prediction_service.predict_and_save(
        image_id=image_id,
        threshold=threshold,
        model_version_name=model_version_name,
    )
