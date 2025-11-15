"""
Tests for patient endpoints and image classification.
"""

import io
from datetime import datetime
from typing import Any, cast

from fastapi.testclient import TestClient
from sqlmodel import Session

from models import Patient, Exam, Image, Pathology, ImagePredictedLabel
from sqlmodel import select


class TestPatientEndpoints:
    """Test suite for patient management endpoints."""

    def test_list_patients_empty(self, client: TestClient):
        """Test listing patients when database is empty."""
        response = client.get("/patients")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_patients_with_data(self, client: TestClient, session: Session):
        """Test listing patients with review status."""
        # Create a patient
        patient = Patient(
            first_name="John",
            last_name="Doe",
            birth_year=1980,
            sex="M",
        )
        session.add(patient)
        session.commit()
        session.refresh(patient)

        # Create exam and image
        patient_id = cast(int, patient.id)
        exam = Exam(patient_id=patient_id)
        session.add(exam)
        session.commit()
        session.refresh(exam)

        exam_id = cast(int, exam.id)
        image = Image(
            exam_id=exam_id,
            filename="test.png",
            image_bytes=b"fake_image_data",
            mime_type="image/png",
        )
        session.add(image)
        session.commit()

        # Test endpoint
        response = client.get("/patients")
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]["first_name"] == "John"
        assert data[0]["last_name"] == "Doe"
        assert data[0]["needs_review"] is True
        assert data[0]["pending_reviews"] == 1

    def test_get_patient_details(self, client: TestClient, session: Session):
        """Test getting patient details with exams."""
        # Create a patient with exam and image
        patient = Patient(
            first_name="Jane",
            last_name="Smith",
            birth_year=1990,
            sex="F",
        )
        session.add(patient)
        session.commit()
        session.refresh(patient)

        patient_id = cast(int, patient.id)
        exam = Exam(patient_id=patient_id, reason="Routine checkup")
        session.add(exam)
        session.commit()
        session.refresh(exam)

        exam_id = cast(int, exam.id)
        image = Image(
            exam_id=exam_id,
            filename="xray.png",
            image_bytes=b"fake_image_data",
            mime_type="image/png",
            view_position="PA",
        )
        session.add(image)
        session.commit()

        # Test endpoint
        response = client.get(f"/patients/{patient.id}")
        assert response.status_code == 200
        data = response.json()

        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Smith"
        assert data["age"] == datetime.now().year - 1990
        assert len(data["exams"]) == 1
        assert data["exams"][0]["reason"] == "Routine checkup"
        assert len(data["exams"][0]["images"]) == 1

    def test_get_nonexistent_patient(self, client: TestClient):
        """Test getting a patient that doesn't exist."""
        response = client.get("/patients/99999")
        assert response.status_code == 404

    def test_create_exam_with_image(
        self, client: TestClient, session: Session, sample_xray_bytes: bytes
    ):
        """Test creating an exam with image upload and ML inference."""
        # Create a patient
        patient = Patient(
            first_name="Test",
            last_name="Patient",
            birth_year=1985,
            sex="M",
        )
        session.add(patient)
        session.commit()
        session.refresh(patient)

        # Upload image
        files = {"file": ("xray.png", io.BytesIO(sample_xray_bytes), "image/png")}
        data = {
            "reason": "Follow-up scan",
            "view_position": "AP",
            "threshold": "0.5",
        }

        response = client.post(f"/patients/{patient.id}/exams", files=files, data=data)

        assert response.status_code == 200
        result = response.json()

        assert "exam_id" in result
        assert result["reason"] == "Follow-up scan"
        assert "image" in result
        assert result["image"]["filename"] == "xray.png"
        assert result["image"]["view_position"] == "AP"
        assert "ml_predictions" in result["image"]

        # Check that predictions were saved
        ml_predictions = result["image"]["ml_predictions"]
        assert "binary_prediction" in ml_predictions
        assert "multi_label_predictions" in ml_predictions

    def test_create_exam_invalid_patient(
        self, client: TestClient, sample_xray_bytes: bytes
    ):
        """Test creating an exam for non-existent patient."""
        files = {"file": ("xray.png", io.BytesIO(sample_xray_bytes), "image/png")}
        data = {"reason": "Test", "threshold": "0.5"}

        response = client.post("/patients/99999/exams", files=files, data=data)
        assert response.status_code == 404

    def test_create_exam_invalid_image(self, client: TestClient, session: Session):
        """Test creating an exam with invalid image."""
        # Create a patient
        patient = Patient(first_name="Test", last_name="User")
        session.add(patient)
        session.commit()
        session.refresh(patient)

        # Try to upload invalid data
        files = {"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
        data = {"threshold": "0.5"}

        response = client.post(f"/patients/{patient.id}/exams", files=files, data=data)
        assert response.status_code == 400

    def test_update_doctor_labels(self, client: TestClient, session: Session):
        """Test updating doctor labels for an image."""
        # Create patient, exam, and image
        patient = Patient(first_name="Test", last_name="User")
        session.add(patient)
        session.commit()
        session.refresh(patient)

        patient_id = cast(int, patient.id)
        exam = Exam(patient_id=patient_id, reason="Routine checkup")
        session.add(exam)
        session.commit()
        session.refresh(exam)

        exam_id = cast(int, exam.id)
        image = Image(
            exam_id=exam_id,
            filename="test.png",
            image_bytes=b"fake_data",
            mime_type="image/png",
        )
        session.add(image)
        session.commit()
        session.refresh(image)

        # Update labels
        labels = {
            "Cardiomegaly": True,
            "Effusion": False,
            "Pneumonia": True,
        }

        response = client.put(
            f"/patients/images/{image.id}/labels",
            json={"labels": labels, "comment": "Confirmed findings"},
        )

        assert response.status_code == 200
        result = response.json()

        assert result["image_id"] == image.id
        assert result["reviewed_at"] is not None
        assert "doctor_labels" in result

        # Verify image was marked as reviewed
        session.refresh(image)
        assert image.reviewed_at is not None

    def test_update_labels_invalid_image(self, client: TestClient):
        """Test updating labels for non-existent image."""
        labels = {"Cardiomegaly": True}

        response = client.put(
            "/patients/images/99999/labels",
            json={"labels": labels},
        )

        assert response.status_code == 404

    def test_update_labels_invalid_pathology(
        self, client: TestClient, session: Session
    ):
        """Test updating labels with invalid pathology code."""
        # Create image
        patient = Patient(first_name="Test", last_name="User")
        session.add(patient)
        session.commit()
        session.refresh(patient)

        patient_id = cast(int, patient.id)
        exam = Exam(patient_id=patient_id)
        session.add(exam)
        session.commit()
        session.refresh(exam)

        exam_id = cast(int, exam.id)
        image = Image(
            exam_id=exam_id,
            filename="test.png",
            image_bytes=b"fake_data",
            mime_type="image/png",
        )
        session.add(image)
        session.commit()
        session.refresh(image)

        # Try to update with invalid pathology
        labels = {"InvalidPathology": True}

        response = client.put(
            f"/patients/images/{image.id}/labels",
            json={"labels": labels},
        )

        assert response.status_code == 400


class TestImageClassification:
    """Test suite for image classification with both models."""

    def test_predict_upload_binary_and_multilabel(
        self, client: TestClient, sample_xray_bytes: bytes
    ):
        """Test prediction endpoint returns both binary and multi-label predictions."""
        files = {"file": ("xray.png", io.BytesIO(sample_xray_bytes), "image/png")}

        response = client.post("/predict", files=files, params={"threshold": 0.5})

        assert response.status_code == 200
        result = response.json()

        assert result["filename"] == "xray.png"
        assert "predictions" in result

        predictions = result["predictions"]
        assert "binary_prediction" in predictions
        assert "multi_label_predictions" in predictions
        assert "threshold" in predictions

        # Check binary prediction structure
        binary = predictions["binary_prediction"]
        assert "label" in binary
        assert "probability" in binary
        assert "has_finding" in binary
        assert isinstance(binary["probability"], float)
        assert isinstance(binary["has_finding"], bool)

        # Check multi-label predictions structure
        multi_label: dict[str, Any] = predictions["multi_label_predictions"]
        assert isinstance(multi_label, dict)

        # Should have predictions for all pathologies
        assert len(multi_label) > 0

        # Each prediction should be an object with probability and predicted_label
        for pred in multi_label.values():
            assert isinstance(pred, dict)
            assert "predicted_label" in pred and "probability" in pred
            predicted_label = cast(bool, pred["predicted_label"])
            probability = cast(float, pred["probability"])
            assert isinstance(predicted_label, bool)
            assert isinstance(probability, float)
            assert 0.0 <= probability <= 1.0

    def test_predict_with_different_thresholds(
        self, client: TestClient, sample_xray_bytes: bytes
    ):
        """Test prediction with different threshold values."""
        files = {"file": ("xray.png", io.BytesIO(sample_xray_bytes), "image/png")}

        # Test with low threshold
        response_low = client.post("/predict", files=files, params={"threshold": 0.1})
        assert response_low.status_code == 200

        # Test with high threshold
        files = {"file": ("xray.png", io.BytesIO(sample_xray_bytes), "image/png")}
        response_high = client.post("/predict", files=files, params={"threshold": 0.9})
        assert response_high.status_code == 200

        # Predictions should differ based on threshold
        result_low = response_low.json()["predictions"]
        result_high = response_high.json()["predictions"]

        assert result_low["threshold"] == 0.1
        assert result_high["threshold"] == 0.9

    def test_predict_stored_image(
        self, client: TestClient, session: Session, sample_xray_bytes: bytes
    ):
        """Test prediction on stored image."""
        # Create patient, exam, and image
        patient = Patient(first_name="Test", last_name="User")
        session.add(patient)
        session.commit()
        session.refresh(patient)

        patient_id = cast(int, patient.id)
        exam = Exam(patient_id=patient_id)
        session.add(exam)
        session.commit()
        session.refresh(exam)

        exam_id = cast(int, exam.id)
        image = Image(
            exam_id=exam_id,
            filename="test.png",
            image_bytes=sample_xray_bytes,
            mime_type="image/png",
        )
        session.add(image)
        session.commit()
        session.refresh(image)

        # Run prediction
        response = client.post(f"/predict/{image.id}", params={"threshold": 0.5})

        assert response.status_code == 200
        result = response.json()

        assert result["image_id"] == image.id
        assert "predictions" in result
        assert "saved_prediction_ids" in result

        # Check that predictions were saved
        assert len(result["saved_prediction_ids"]) > 0

    def test_predict_invalid_image(self, client: TestClient):
        """Test prediction with invalid image data."""
        files = {"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}

        response = client.post("/predict", files=files)
        assert response.status_code == 400

    def test_predict_nonexistent_stored_image(self, client: TestClient):
        """Test prediction on non-existent stored image."""
        response = client.post("/predict/99999")
        assert response.status_code == 404

    def test_predictions_saved_to_database(
        self, client: TestClient, session: Session, sample_xray_bytes: bytes
    ):
        """Test that predictions are correctly saved to database."""
        # Create patient and upload exam
        patient = Patient(first_name="Test", last_name="User")
        session.add(patient)
        session.commit()
        session.refresh(patient)

        files = {"file": ("xray.png", io.BytesIO(sample_xray_bytes), "image/png")}
        data = {"threshold": "0.5"}

        response = client.post(f"/patients/{patient.id}/exams", files=files, data=data)
        assert response.status_code == 200

        result = response.json()
        image_id = result["image"]["id"]

        # Verify predictions in database
        predictions = list(
            session.exec(
                select(ImagePredictedLabel).where(
                    ImagePredictedLabel.image_id == image_id
                )
            )
        )

        # Should have at least one prediction (binary + multi-label)
        assert len(predictions) > 0

        # Check that we have both binary and multi-label predictions
        pathology_codes: set[str] = set()
        for pred in predictions:
            pathology = session.get(Pathology, pred.pathology_id)
            if pathology is not None:
                pathology_codes.add(pathology.code)

        # Should include ANY_PATHOLOGY (binary) and multi-label pathologies
        assert "ANY_PATHOLOGY" in pathology_codes

        # Should have multiple pathologies predicted
        assert len(pathology_codes) > 1


class TestEndToEndWorkflow:
    """Test complete workflow from upload to review."""

    def test_complete_review_workflow(
        self, client: TestClient, session: Session, sample_xray_bytes: bytes
    ):
        """Test complete workflow: create patient, upload exam, review labels."""
        # 1. Create patient (via database for simplicity)
        patient = Patient(
            first_name="Jane",
            last_name="Doe",
            birth_year=1985,
            sex="F",
        )
        session.add(patient)
        session.commit()
        session.refresh(patient)

        # 2. List patients - should show needs review = False
        response = client.get("/patients")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["needs_review"] is False

        # 3. Upload new exam with image
        files = {"file": ("xray.png", io.BytesIO(sample_xray_bytes), "image/png")}
        data = {
            "reason": "Annual checkup",
            "view_position": "PA",
            "threshold": "0.5",
        }

        response = client.post(f"/patients/{patient.id}/exams", files=files, data=data)
        assert response.status_code == 200
        result = response.json()
        image_id = result["image"]["id"]

        # 4. List patients - should now show needs review = True
        response = client.get("/patients")
        assert response.status_code == 200
        patients = response.json()
        assert patients[0]["needs_review"] is True
        assert patients[0]["pending_reviews"] == 1

        # 5. Get patient details to see ML predictions
        response = client.get(f"/patients/{patient.id}")
        assert response.status_code == 200
        patient_data = response.json()

        image_data = patient_data["exams"][0]["images"][0]
        assert image_data["is_pending"] is True
        assert "ml_predictions" in image_data

        # 6. Doctor reviews and confirms/edits labels
        labels = {
            "Cardiomegaly": True,
            "Effusion": False,
        }

        response = client.put(
            f"/patients/images/{image_id}/labels",
            json={"labels": labels, "comment": "Confirmed cardiomegaly"},
        )
        assert response.status_code == 200

        # 7. List patients - should now show needs review = False
        response = client.get("/patients")
        assert response.status_code == 200
        patients = response.json()
        assert patients[0]["needs_review"] is False
        assert patients[0]["pending_reviews"] == 0

        # 8. Get patient details - image should be marked as reviewed
        response = client.get(f"/patients/{patient.id}")
        assert response.status_code == 200
        patient_data = response.json()

        image_data = patient_data["exams"][0]["images"][0]
        assert image_data["is_pending"] is False
        assert image_data["reviewed_at"] is not None
        assert "doctor_labels" in image_data
        assert len(image_data["doctor_labels"]) > 0
