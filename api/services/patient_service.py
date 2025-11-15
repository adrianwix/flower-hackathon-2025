"""
Patient service for managing patient records, exams, and images.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, cast

from fastapi import HTTPException
from sqlmodel import Session, select, func, col

from config import DEFAULT_MODEL_VERSION
from models import (
    Patient,
    Exam,
    Image,
    ImagePredictedLabel,
    DoctorLabel,
    ModelVersion,
    Pathology,
    User,
)
from ml.inference import predict_image
from ml.preprocessing import validate_image as ml_validate_image


class PatientService:
    """Service for handling patient-related operations."""

    def __init__(self, session: Session):
        """
        Initialize patient service.

        Args:
            session: Database session
        """
        self.session = session

    async def list_patients_with_status(self) -> List[Dict[str, Any]]:
        """
        List all patients with review status.

        Returns:
            List of patients with review status
        """
        # Get all patients
        patients = self.session.exec(select(Patient)).all()

        result: List[Dict[str, Any]] = []
        for patient in patients:
            # Get latest exam
            latest_exam = self.session.exec(
                select(Exam)
                .where(Exam.patient_id == patient.id)
                .order_by(col(Exam.exam_datetime).desc())
            ).first()

            # Count pending reviews (images without reviewed_at)
            pending_count = self.session.exec(
                select(func.count(col(Image.id)))
                .join(Exam)
                .where(Exam.patient_id == patient.id)
                .where(col(Image.reviewed_at).is_(None))
            ).one()

            # Calculate age
            age = None
            if patient.birth_year:
                current_year = datetime.now(timezone.utc).year
                age = current_year - patient.birth_year

            patient_data: Dict[str, Any] = {
                "id": patient.id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "age": age,
                "sex": patient.sex,
                "needs_review": pending_count > 0,
                "pending_reviews": pending_count,
                "last_follow_up_date": latest_exam.exam_datetime
                if latest_exam
                else None,
            }
            result.append(patient_data)

        # Sort by needs_review (True first), then by last_follow_up_date
        result.sort(
            key=lambda x: (
                not x["needs_review"],
                x["last_follow_up_date"]
                if x["last_follow_up_date"] is not None
                else datetime.min.replace(tzinfo=timezone.utc),
            ),
            reverse=True,
        )

        return result

    async def get_patient_with_exams(self, patient_id: int) -> Dict[str, Any]:
        """
        Get patient details with all exams and images.

        Args:
            patient_id: Patient ID

        Returns:
            Patient details with exams
        """
        # Get patient
        patient = self.session.get(Patient, patient_id)
        if not patient:
            raise HTTPException(
                status_code=404, detail=f"Patient {patient_id} not found"
            )

        # Get all exams with images
        exams = self.session.exec(
            select(Exam)
            .where(Exam.patient_id == patient_id)
            .order_by(col(Exam.exam_datetime).desc())
        ).all()

        exams_data: List[Dict[str, Any]] = []
        for exam in exams:
            # Get images for this exam
            images = self.session.exec(
                select(Image).where(Image.exam_id == exam.id)
            ).all()

            images_data: List[Dict[str, Any]] = []
            for image in images:
                # Get ML predictions
                image_id = cast(int, image.id)
                ml_predictions = self._get_ml_predictions(image_id)

                # Get doctor labels
                doctor_labels = self._get_doctor_labels(image_id)

                image_data: Dict[str, Any] = {
                    "id": image.id,
                    "filename": image.filename,
                    "view_position": image.view_position,
                    "reviewed_at": image.reviewed_at,
                    "is_pending": image.reviewed_at is None,
                    "ml_predictions": ml_predictions,
                    "doctor_labels": doctor_labels,
                }
                images_data.append(image_data)

            exam_data: Dict[str, Any] = {
                "id": exam.id,
                "exam_datetime": exam.exam_datetime,
                "reason": exam.reason,
                "images": images_data,
            }
            exams_data.append(exam_data)

        # Calculate age
        age = None
        if patient.birth_year:
            current_year = datetime.now(timezone.utc).year
            age = current_year - patient.birth_year

        return {
            "id": patient.id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "age": age,
            "birth_year": patient.birth_year,
            "sex": patient.sex,
            "external_patient_id": patient.external_patient_id,
            "exams": exams_data,
        }

    async def create_exam_with_image(
        self,
        patient_id: int,
        image_bytes: bytes,
        filename: str,
        exam_datetime: Optional[datetime] = None,
        reason: Optional[str] = None,
        view_position: Optional[str] = None,
        threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Create a new exam with image and run ML inference.

        Args:
            patient_id: Patient ID
            image_bytes: Raw image bytes
            filename: Image filename
            exam_datetime: Exam datetime (defaults to now)
            reason: Reason for exam
            view_position: X-ray view position
            threshold: Probability threshold for predictions

        Returns:
            Created exam with predictions
        """
        # Validate patient exists
        patient = self.session.get(Patient, patient_id)
        if not patient:
            raise HTTPException(
                status_code=404, detail=f"Patient {patient_id} not found"
            )

        # Validate image
        is_valid, error_message = ml_validate_image(image_bytes)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)

        # Create exam
        exam = Exam(
            patient_id=patient_id,
            exam_datetime=exam_datetime or datetime.now(timezone.utc),
            reason=reason,
        )
        self.session.add(exam)
        self.session.flush()

        # Create image
        mime_type = "image/png"
        if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
            mime_type = "image/jpeg"

        exam_id = cast(int, exam.id)
        image = Image(
            exam_id=exam_id,
            filename=filename,
            image_bytes=image_bytes,
            mime_type=mime_type,
            view_position=view_position,
        )
        self.session.add(image)
        self.session.flush()

        # Run ML inference
        predictions = await predict_image(image_bytes, threshold=threshold)

        # Save predictions to database
        model_version = self._get_or_create_model_version(DEFAULT_MODEL_VERSION)
        image_id = cast(int, image.id)
        self._save_predictions(image_id, model_version, predictions)

        self.session.commit()
        self.session.refresh(image)
        self.session.refresh(exam)

        # Get saved predictions
        image_id = cast(int, image.id)
        ml_predictions = self._get_ml_predictions(image_id)

        return {
            "exam_id": exam.id,
            "exam_datetime": exam.exam_datetime,
            "reason": exam.reason,
            "image": {
                "id": image.id,
                "filename": image.filename,
                "view_position": image.view_position,
                "ml_predictions": ml_predictions,
            },
        }

    async def update_doctor_labels(
        self,
        image_id: int,
        labels: Dict[str, bool],
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update doctor labels for an image.

        Args:
            image_id: Image ID
            labels: Dictionary of pathology codes to boolean values
            comment: Optional comment

        Returns:
            Updated doctor labels
        """
        # Get image
        image = self.session.get(Image, image_id)
        if not image:
            raise HTTPException(status_code=404, detail=f"Image {image_id} not found")

        # Get or create default doctor user (for hackathon - no real auth)
        doctor = self._get_or_create_default_doctor()

        # Get model version
        model_version = self._get_or_create_model_version(DEFAULT_MODEL_VERSION)

        # Update or create doctor labels
        for pathology_code, is_present in labels.items():
            # Get pathology
            pathology = self.session.exec(
                select(Pathology).where(Pathology.code == pathology_code)
            ).first()

            if not pathology:
                # Try to match display name
                pathology = self.session.exec(
                    select(Pathology).where(Pathology.display_name == pathology_code)
                ).first()

            if not pathology:
                raise HTTPException(
                    status_code=400, detail=f"Unknown pathology: {pathology_code}"
                )

            # Check if doctor label already exists
            existing_label = self.session.exec(
                select(DoctorLabel).where(
                    DoctorLabel.image_id == image_id,
                    DoctorLabel.model_version_id == model_version.id,
                    DoctorLabel.pathology_id == pathology.id,
                    DoctorLabel.labeled_by == doctor.id,
                )
            ).first()

            if existing_label:
                # Update existing label
                existing_label.is_present = is_present
                existing_label.comment = comment
                existing_label.labeled_at = datetime.now(timezone.utc)
            else:
                # Create new label
                model_version_id = cast(int, model_version.id)
                pathology_id = cast(int, pathology.id)
                doctor_id = cast(int, doctor.id)
                doctor_label = DoctorLabel(
                    image_id=image_id,
                    model_version_id=model_version_id,
                    pathology_id=pathology_id,
                    is_present=is_present,
                    comment=comment,
                    labeled_by=doctor_id,
                )
                self.session.add(doctor_label)

        # Mark image as reviewed
        image.reviewed_at = datetime.now(timezone.utc)
        self.session.add(image)

        self.session.commit()

        # Get updated doctor labels
        doctor_labels = self._get_doctor_labels(image_id)

        return {
            "image_id": image_id,
            "reviewed_at": image.reviewed_at,
            "doctor_labels": doctor_labels,
        }

    def _get_ml_predictions(self, image_id: int) -> Dict[str, Any]:
        """
        Get ML predictions for an image.

        Args:
            image_id: Image ID

        Returns:
            Dictionary with binary and multi-label predictions
        """
        predictions = self.session.exec(
            select(ImagePredictedLabel, Pathology)
            .join(Pathology)
            .where(ImagePredictedLabel.image_id == image_id)
        ).all()

        binary_prediction: Optional[Dict[str, Any]] = None
        multi_label_predictions: Dict[str, Dict[str, Any]] = {}

        for pred, pathology in predictions:
            if pathology.code == "ANY_PATHOLOGY":
                binary_prediction = {
                    "pathology": pathology.code,
                    "probability": pred.probability,
                    "predicted_label": pred.predicted_label,
                }
            else:
                multi_label_predictions[pathology.code] = {
                    "probability": pred.probability,
                    "predicted_label": pred.predicted_label,
                }

        return {
            "binary_prediction": binary_prediction,
            "multi_label_predictions": multi_label_predictions,
        }

    def _get_doctor_labels(self, image_id: int) -> Dict[str, Any]:
        """
        Get doctor labels for an image.

        Args:
            image_id: Image ID

        Returns:
            Dictionary of doctor labels
        """
        labels = self.session.exec(
            select(DoctorLabel, Pathology)
            .join(Pathology)
            .where(DoctorLabel.image_id == image_id)
        ).all()

        result: Dict[str, Dict[str, Any]] = {}
        for label, pathology in labels:
            result[pathology.code] = {
                "is_present": label.is_present,
                "comment": label.comment,
                "labeled_at": label.labeled_at,
            }

        return result

    def _get_or_create_model_version(self, model_version_name: str) -> ModelVersion:
        """
        Get or create a model version.

        Args:
            model_version_name: Name of the model version

        Returns:
            ModelVersion instance
        """
        # Try to get existing model version first
        model_version = self.session.exec(
            select(ModelVersion).where(ModelVersion.name == model_version_name)
        ).first()

        if model_version:
            return model_version

        # Create new model version
        try:
            model_version = ModelVersion(
                name=model_version_name,
                description="Dual model: Binary classifier + Multi-label classifier",
            )
            self.session.add(model_version)
            self.session.flush()
            return model_version
        except Exception:
            # If concurrent insert happened, rollback and query again
            self.session.rollback()
            model_version = self.session.exec(
                select(ModelVersion).where(ModelVersion.name == model_version_name)
            ).first()
            if not model_version:
                raise
            return model_version

    def _get_or_create_default_doctor(self) -> User:
        """
        Get or create a default doctor user (for hackathon).

        Returns:
            User instance
        """
        # Try to get existing doctor first
        doctor = self.session.exec(
            select(User).where(User.email == "doctor@example.com")
        ).first()

        if doctor:
            return doctor

        # Create new doctor
        try:
            doctor = User(
                email="doctor@example.com",
                full_name="Dr. Demo",
                password_hash="fake_hash_for_hackathon",
                role="doctor",
            )
            self.session.add(doctor)
            self.session.flush()
            return doctor
        except Exception:
            # If concurrent insert happened, rollback and query again
            self.session.rollback()
            doctor = self.session.exec(
                select(User).where(User.email == "doctor@example.com")
            ).first()
            if not doctor:
                raise
            return doctor

    def _save_predictions(
        self,
        image_id: int,
        model_version: ModelVersion,
        predictions: Dict[str, Any],
    ) -> None:
        """
        Save predictions to database.

        Args:
            image_id: Image ID
            model_version: Model version instance
            predictions: Prediction results
        """
        # Save binary prediction
        binary_pred = predictions["binary_prediction"]

        # Get or create ANY_PATHOLOGY pathology
        any_pathology = self.session.exec(
            select(Pathology).where(Pathology.code == "ANY_PATHOLOGY")
        ).first()

        if not any_pathology:
            any_pathology = Pathology(
                code="ANY_PATHOLOGY",
                display_name="Any Pathology",
                description="Binary classification: Finding vs No Finding",
            )
            self.session.add(any_pathology)
            self.session.flush()

        # Save binary prediction
        model_version_id = cast(int, model_version.id)
        any_pathology_id = cast(int, any_pathology.id)
        binary_label = ImagePredictedLabel(
            image_id=image_id,
            model_version_id=model_version_id,
            pathology_id=any_pathology_id,
            probability=binary_pred["probability"],
            predicted_label=binary_pred["has_finding"],
        )
        self.session.add(binary_label)

        # Save multi-label predictions (predictions are JSON-friendly objects)
        for pathology_code, pred in predictions["multi_label_predictions"].items():
            probability = pred.get("probability")
            predicted_label = pred.get("predicted_label")

            pathology = self.session.exec(
                select(Pathology).where(Pathology.code == pathology_code)
            ).first()

            if pathology:
                pathology_id = cast(int, pathology.id)
                pred_label = ImagePredictedLabel(
                    image_id=image_id,
                    model_version_id=model_version_id,
                    pathology_id=pathology_id,
                    probability=probability,
                    predicted_label=predicted_label,
                )
                self.session.add(pred_label)

        self.session.flush()
