"""
Example usage of the radiology review API models and prediction service.

This script demonstrates:
1. Creating database records (users, patients, exams, images)
2. Running predictions on images
3. Querying prediction results
"""

from datetime import datetime

from sqlmodel import Session, select

from database import create_db_and_tables, engine, init_pathologies
from models import (
    User,
    Patient,
    Exam,
    Image,
    Pathology,
    ModelVersion,
    ImagePredictedLabel,
    ReviewStatus,
)
from model_service import get_model


def create_sample_data(session: Session):
    """Create sample data for demonstration"""

    # Create a doctor user
    doctor = User(
        email="dr.smith@hospital.com",
        full_name="Dr. Jane Smith",
        password_hash="dummy_hash_for_demo",  # In production, use proper password hashing
        role="doctor",
    )
    session.add(doctor)
    session.commit()
    session.refresh(doctor)
    print(f"✓ Created doctor: {doctor.full_name} (ID: {doctor.id})")

    # Create a patient
    patient = Patient(
        external_patient_id="NIH_00001",
        first_name="John",
        last_name="Doe",
        birth_year=1975,
        sex="M",
    )
    session.add(patient)
    session.commit()
    session.refresh(patient)
    print(
        f"✓ Created patient: {patient.first_name} {patient.last_name} (ID: {patient.id})"
    )

    # Create an exam
    exam = Exam(
        patient_id=patient.id,
        exam_datetime=datetime.utcnow(),
        reason="Routine chest X-ray",
        created_by=doctor.id,
    )
    session.add(exam)
    session.commit()
    session.refresh(exam)
    print(f"✓ Created exam (ID: {exam.id})")

    # Create a sample image (mock bytes for demo)
    # In production, this would be actual X-ray image bytes
    sample_image_bytes = b"mock_xray_image_bytes"

    image = Image(
        exam_id=exam.id,
        filename="sample_xray.png",
        image_bytes=sample_image_bytes,
        mime_type="image/png",
        view_position="PA",
        ground_truth_labels=["Cardiomegaly"],  # Example ground truth
        review_status=ReviewStatus.PENDING.value,
    )
    session.add(image)
    session.commit()
    session.refresh(image)
    print(f"✓ Created image: {image.filename} (ID: {image.id})")

    return doctor, patient, exam, image


def run_prediction_example(session: Session, image: Image):
    """Run prediction on an image and store results"""

    print("\n--- Running Predictions ---")

    # Get or create model version
    model_version = ModelVersion(
        name="mock_v1",
        description="Mock model for demonstration",
    )
    session.add(model_version)
    session.commit()
    session.refresh(model_version)
    print(f"✓ Created model version: {model_version.name} (ID: {model_version.id})")

    # Get the ML model
    model = get_model()

    # Run prediction
    predictions = model.predict_all(image.image_bytes, threshold=0.5)
    print("\n📊 Prediction Results:")
    print(
        f"  Binary (Any Finding): {predictions['binary_prediction']['has_finding']} "
        f"(prob: {predictions['binary_prediction']['probability']:.3f})"
    )

    # Save binary prediction
    any_pathology = session.exec(
        select(Pathology).where(Pathology.code == "ANY_PATHOLOGY")
    ).first()

    if any_pathology:
        binary_pred = ImagePredictedLabel(
            image_id=image.id,
            model_version_id=model_version.id,
            pathology_id=any_pathology.id,
            probability=predictions["binary_prediction"]["probability"],
            predicted_label=predictions["binary_prediction"]["has_finding"],
        )
        session.add(binary_pred)

    # Save multi-label predictions (only positive ones for brevity)
    print("\n  Multi-label predictions (positive only):")
    positive_count = 0
    for pathology_code, (predicted_label, probability) in predictions[
        "multi_label_predictions"
    ].items():
        if predicted_label:
            pathology = session.exec(
                select(Pathology).where(Pathology.code == pathology_code)
            ).first()

            if pathology:
                pred_label = ImagePredictedLabel(
                    image_id=image.id,
                    model_version_id=model_version.id,
                    pathology_id=pathology.id,
                    probability=probability,
                    predicted_label=predicted_label,
                )
                session.add(pred_label)
                print(f"    - {pathology.display_name}: {probability:.3f}")
                positive_count += 1

    if positive_count == 0:
        print("    (No positive predictions)")

    session.commit()
    print(f"\n✓ Saved {positive_count + 1} predictions to database")


def query_predictions(session: Session, image: Image):
    """Query and display predictions for an image"""

    print("\n--- Querying Stored Predictions ---")

    predictions = session.exec(
        select(ImagePredictedLabel).where(ImagePredictedLabel.image_id == image.id)
    ).all()

    print(f"Found {len(predictions)} predictions for image {image.id}:")
    for pred in predictions:
        pathology = session.get(Pathology, pred.pathology_id)
        model = session.get(ModelVersion, pred.model_version_id)
        print(
            f"  - {pathology.display_name}: {pred.predicted_label} "
            f"(prob: {pred.probability:.3f}, model: {model.name})"
        )


def main():
    """Main example function"""

    print("=== Radiology Review API - Example Usage ===\n")

    # Initialize database
    print("Initializing database...")
    create_db_and_tables()

    with Session(engine) as session:
        # Initialize pathologies
        init_pathologies(session)
        print("✓ Database initialized\n")

        # Create sample data
        print("--- Creating Sample Data ---")
        doctor, patient, exam, image = create_sample_data(session)

        # Run predictions
        run_prediction_example(session, image)

        # Query predictions
        query_predictions(session, image)

        print("\n✅ Example completed successfully!")
        print("\nYou can now:")
        print("  1. Start the API: uvicorn main:app --reload")
        print("  2. Visit http://localhost:8000/docs for interactive API docs")
        print("  3. Use POST /predict to test with real images")


if __name__ == "__main__":
    main()
