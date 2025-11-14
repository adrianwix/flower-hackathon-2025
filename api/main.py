from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from database import create_db_and_tables, get_session, init_pathologies
from models import (
    Image,
    ImagePredictedLabel,
    ModelVersion,
    Pathology,
    ReviewStatus,
)
from model_service import predict_image, validate_image


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Create tables and initialize data
    create_db_and_tables()

    # Initialize pathologies if needed
    with Session(get_session().__next__()) as session:
        init_pathologies(session)

    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="Flower Hackathon API - Radiology Review System",
    description="API for managing patient X-ray records and AI-assisted pathology detection",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Flower Hackathon API - Radiology Review System",
        "version": "0.1.0",
    }


# =========================================================
# Prediction Endpoints
# =========================================================


@app.post("/predict")
async def predict_xray(
    file: UploadFile = File(...),
    threshold: float = 0.5,
    session: Session = Depends(get_session),
):
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
    is_valid, error_message = validate_image(image_bytes)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    # Run prediction
    predictions = await predict_image(image_bytes, threshold=threshold)

    return {
        "filename": file.filename,
        "predictions": predictions,
    }


@app.post("/images/{image_id}/predict")
async def predict_stored_image(
    image_id: int,
    threshold: float = 0.5,
    model_version_name: Optional[str] = None,
    session: Session = Depends(get_session),
):
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
    # Get image from database
    image = session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f"Image {image_id} not found")

    # Get or create model version
    if model_version_name is None:
        model_version_name = "mock_v1"

    model_version = session.exec(
        select(ModelVersion).where(ModelVersion.name == model_version_name)
    ).first()

    if not model_version:
        model_version = ModelVersion(
            name=model_version_name,
            description="Mock model for demonstration purposes",
        )
        session.add(model_version)
        session.commit()
        session.refresh(model_version)

    # Run prediction
    predictions = await predict_image(image.image_bytes, threshold=threshold)

    # Save binary prediction (ANY_PATHOLOGY)
    any_pathology = session.exec(
        select(Pathology).where(Pathology.code == "ANY_PATHOLOGY")
    ).first()

    if any_pathology:
        binary_pred = predictions["binary_prediction"]

        # Check if prediction already exists
        existing_pred = session.exec(
            select(ImagePredictedLabel).where(
                ImagePredictedLabel.image_id == image_id,
                ImagePredictedLabel.model_version_id == model_version.id,
                ImagePredictedLabel.pathology_id == any_pathology.id,
            )
        ).first()

        if existing_pred:
            # Update existing prediction
            existing_pred.probability = binary_pred["probability"]
            existing_pred.predicted_label = binary_pred["has_finding"]
        else:
            # Create new prediction
            pred_label = ImagePredictedLabel(
                image_id=image_id,
                model_version_id=model_version.id,
                pathology_id=any_pathology.id,
                probability=binary_pred["probability"],
                predicted_label=binary_pred["has_finding"],
            )
            session.add(pred_label)

    # Save multi-label predictions
    saved_predictions = []
    for pathology_code, (predicted_label, probability) in predictions[
        "multi_label_predictions"
    ].items():
        pathology = session.exec(
            select(Pathology).where(Pathology.code == pathology_code)
        ).first()

        if pathology:
            # Check if prediction already exists
            existing_pred = session.exec(
                select(ImagePredictedLabel).where(
                    ImagePredictedLabel.image_id == image_id,
                    ImagePredictedLabel.model_version_id == model_version.id,
                    ImagePredictedLabel.pathology_id == pathology.id,
                )
            ).first()

            if existing_pred:
                # Update existing prediction
                existing_pred.probability = probability
                existing_pred.predicted_label = predicted_label
                saved_predictions.append(existing_pred.id)
            else:
                # Create new prediction
                pred_label = ImagePredictedLabel(
                    image_id=image_id,
                    model_version_id=model_version.id,
                    pathology_id=pathology.id,
                    probability=probability,
                    predicted_label=predicted_label,
                )
                session.add(pred_label)
                session.flush()
                saved_predictions.append(pred_label.id)

    # Update image review status
    image.review_status = ReviewStatus.PENDING.value

    session.commit()

    return {
        "image_id": image_id,
        "model_version": model_version_name,
        "predictions": predictions,
        "saved_prediction_ids": saved_predictions,
    }


@app.get("/pathologies")
async def list_pathologies(session: Session = Depends(get_session)):
    """
    List all available pathology codes.

    Returns:
        List of all pathologies in the system
    """
    pathologies = session.exec(select(Pathology)).all()
    return {"pathologies": pathologies}


@app.get("/model-versions")
async def list_model_versions(session: Session = Depends(get_session)):
    """
    List all available model versions.

    Returns:
        List of all model versions in the system
    """
    versions = session.exec(select(ModelVersion)).all()
    return {"model_versions": versions}
