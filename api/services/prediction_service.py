"""
Prediction service for ML inference and database persistence.
"""

from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from sqlmodel import Session, select

from config import DEFAULT_MODEL_VERSION
from models import (
    Image,
    ImagePredictedLabel,
    ModelVersion,
    Pathology,
)
from ml.inference import predict_image


class PredictionService:
    """Service for handling ML predictions and saving results."""

    def __init__(self, session: Session):
        """
        Initialize prediction service.

        Args:
            session: Database session
        """
        self.session = session

    async def predict_upload(
        self, image_bytes: bytes, threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Run prediction on uploaded image bytes (no DB persistence).

        Args:
            image_bytes: Raw image bytes
            threshold: Probability threshold for positive predictions

        Returns:
            Prediction results
        """
        predictions = await predict_image(image_bytes, threshold=threshold)
        return predictions

    async def predict_and_save(
        self,
        image_id: int,
        threshold: float = 0.5,
        model_version_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run prediction on stored image and save results to database.

        Args:
            image_id: ID of the image in the database
            threshold: Probability threshold for positive predictions
            model_version_name: Name of the model version

        Returns:
            Prediction results with database record IDs
        """
        # Get image from database
        image = self.session.get(Image, image_id)
        if not image:
            raise HTTPException(status_code=404, detail=f"Image {image_id} not found")

        # Get or create model version
        if model_version_name is None:
            model_version_name = DEFAULT_MODEL_VERSION

        model_version = self._get_or_create_model_version(model_version_name)

        # Run prediction
        predictions = await predict_image(image.image_bytes, threshold=threshold)

        # Save binary prediction (ANY_PATHOLOGY)
        self._save_binary_prediction(
            image_id, model_version, predictions["binary_prediction"]
        )

        # Save multi-label predictions
        saved_predictions = self._save_multi_label_predictions(
            image_id, model_version, predictions["multi_label_predictions"]
        )

        self.session.commit()

        return {
            "image_id": image_id,
            "model_version": model_version_name,
            "predictions": predictions,
            "saved_prediction_ids": saved_predictions,
        }

    def _get_or_create_model_version(self, model_version_name: str) -> ModelVersion:
        """
        Get or create a model version.

        Args:
            model_version_name: Name of the model version

        Returns:
            ModelVersion instance
        """
        model_version = self.session.exec(
            select(ModelVersion).where(ModelVersion.name == model_version_name)
        ).first()

        if model_version:
            return model_version

        # Only create if not found, and do NOT set id manually
        new_model_version = ModelVersion(
            name=model_version_name,
            description="Mock model for demonstration purposes",
        )
        self.session.add(new_model_version)
        self.session.commit()
        self.session.refresh(new_model_version)
        return new_model_version

    def _save_binary_prediction(
        self,
        image_id: int,
        model_version: ModelVersion,
        binary_pred: Dict[str, Any],
    ) -> None:
        """
        Save binary prediction (ANY_PATHOLOGY) to database.

        Args:
            image_id: Image ID
            model_version: Model version instance
            binary_pred: Binary prediction dictionary
        """
        any_pathology = self.session.exec(
            select(Pathology).where(Pathology.code == "ANY_PATHOLOGY")
        ).first()

        if (
            any_pathology
            and any_pathology.id is not None
            and model_version.id is not None
        ):
            # Check if prediction already exists
            existing_pred = self.session.exec(
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
                self.session.add(pred_label)

    def _save_multi_label_predictions(
        self,
        image_id: int,
        model_version: ModelVersion,
        multi_label_predictions: Dict[str, Dict[str, object]],
    ) -> List[int]:
        """
        Save multi-label predictions to database.

        Args:
            image_id: Image ID
            model_version: Model version instance
            multi_label_predictions: Dictionary of pathology predictions

        Returns:
            List of saved prediction IDs
        """
        saved_predictions: List[int] = []

        for pathology_code, pred in multi_label_predictions.items():
            raw_predicted_label = pred.get("predicted_label", False)
            predicted_label = (
                bool(raw_predicted_label) if raw_predicted_label is not None else False
            )

            raw_probability = pred.get("probability", 0.0)
            if isinstance(raw_probability, (int, float)):
                probability = float(raw_probability)
            elif isinstance(raw_probability, str):
                try:
                    probability = float(raw_probability)
                except ValueError:
                    probability = 0.0
            else:
                probability = 0.0
            pathology = self.session.exec(
                select(Pathology).where(Pathology.code == pathology_code)
            ).first()

            if pathology and pathology.id is not None:
                # Check if prediction already exists
                existing_pred = self.session.exec(
                    select(ImagePredictedLabel).where(
                        ImagePredictedLabel.image_id == image_id,
                        ImagePredictedLabel.model_version_id == model_version.id,
                        ImagePredictedLabel.pathology_id == pathology.id,
                    )
                ).first()

                print(
                    f"[DEBUG] pathology_code={pathology_code}, probability={probability} ({type(probability)}), predicted_label={predicted_label} ({type(predicted_label)})"
                )
                if existing_pred and existing_pred.id is not None:
                    # Update existing prediction
                    print(f"[DEBUG] Updating existing_pred.id={existing_pred.id}")
                    existing_pred.probability = probability
                    existing_pred.predicted_label = predicted_label
                    saved_predictions.append(existing_pred.id)
                else:
                    # Create new prediction
                    if model_version.id is None:
                        continue
                    print(
                        f"[DEBUG] Creating new ImagePredictedLabel for pathology_id={pathology.id}"
                    )
                    pred_label = ImagePredictedLabel(
                        image_id=image_id,
                        model_version_id=model_version.id,
                        pathology_id=pathology.id,
                        probability=probability,
                        predicted_label=predicted_label,
                    )
                    self.session.add(pred_label)
                    self.session.flush()
                    if pred_label.id is not None:
                        saved_predictions.append(pred_label.id)

        return saved_predictions
