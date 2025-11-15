"""
Seed data loader for the radiology review application.

Loads patients, exams, images, model versions, predicted labels, and doctor labels
from JSON files in the seeds/ directory.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from sqlmodel import Session, select

from models import (
    Patient,
    Exam,
    Image,
    Pathology,
    ModelVersion,
    ImagePredictedLabel,
    DoctorLabel,
)


def load_seed_data(session: Session, seeds_dir: Path) -> dict[str, int]:
    """
    Load seed data from JSON files into the database.

    Returns a dictionary with counts of loaded records.
    """
    stats: dict[str, int] = {
        "patients": 0,
        "exams": 0,
        "images": 0,
        "model_versions": 0,
        "predicted_labels": 0,
        "doctor_labels": 0,
        "skipped_patients": 0,
        "skipped_exams": 0,
        "skipped_images": 0,
        "skipped_model_versions": 0,
    }

    # Load patients
    patients_file = seeds_dir / "patients.json"
    if patients_file.exists():
        print(f"Loading patients from {patients_file}...")
        with open(patients_file) as f:
            patients_data = json.load(f)

        for patient_data in patients_data:
            # Check if patient already exists
            existing = session.exec(
                select(Patient).where(Patient.id == patient_data["id"])
            ).first()

            if existing:
                stats["skipped_patients"] += 1
                continue

            patient = Patient(
                id=patient_data["id"],
                external_patient_id=patient_data["external_patient_id"],
                first_name=patient_data.get("first_name"),
                last_name=patient_data.get("last_name"),
                birth_year=patient_data.get("birth_year"),
                sex=patient_data.get("sex"),
            )
            session.add(patient)
            stats["patients"] += 1

        session.commit()
        print(
            f"  ✓ Loaded {stats['patients']} patients (skipped {stats['skipped_patients']} existing)"
        )

    # Load exams
    exams_file = seeds_dir / "exams.json"
    if exams_file.exists():
        print(f"Loading exams from {exams_file}...")
        with open(exams_file) as f:
            exams_data = json.load(f)

        for exam_data in exams_data:
            # Check if exam already exists
            existing = session.exec(
                select(Exam).where(Exam.id == exam_data["id"])
            ).first()

            if existing:
                stats["skipped_exams"] += 1
                continue

            exam = Exam(
                id=exam_data["id"],
                patient_id=exam_data["patient_id"],
                exam_datetime=datetime.now(timezone.utc),
                reason=exam_data.get("reason"),
                created_by=exam_data.get("created_by"),
            )
            session.add(exam)
            stats["exams"] += 1

        session.commit()
        print(
            f"  ✓ Loaded {stats['exams']} exams (skipped {stats['skipped_exams']} existing)"
        )

    # Load images
    images_file = seeds_dir / "images.json"
    images_dir = seeds_dir / "images"

    if images_file.exists() and images_dir.exists():
        print(f"Loading images from {images_file}...")
        with open(images_file) as f:
            images_data = json.load(f)

        for idx, image_data in enumerate(images_data, 1):
            # Read image bytes
            image_path = images_dir / image_data["filename"]
            if not image_path.exists():
                print(f"  ⚠️  Image file not found: {image_data['filename']}")
                stats["skipped_images"] += 1
                continue

            # Check if image already exists (by id if provided, otherwise by exam_id and filename)
            if "id" in image_data:
                existing = session.exec(
                    select(Image).where(Image.id == image_data["id"])
                ).first()
            else:
                existing = session.exec(
                    select(Image).where(
                        Image.exam_id == image_data["exam_id"],
                        Image.filename == image_data["filename"],
                    )
                ).first()

            if existing:
                stats["skipped_images"] += 1
                continue

            with open(image_path, "rb") as f:
                image_bytes = f.read()

            image = Image(
                id=image_data.get("id"),  # Use provided ID if available
                exam_id=image_data["exam_id"],
                filename=image_data["filename"],
                image_bytes=image_bytes,
                mime_type="image/png",
                view_position=image_data.get("view_position"),
            )
            session.add(image)
            stats["images"] += 1

            # Commit in batches to avoid memory issues
            if idx % 100 == 0:
                session.commit()
                print(f"  Progress: {idx}/{len(images_data)} images...")

        session.commit()
        print(
            f"  ✓ Loaded {stats['images']} images (skipped {stats['skipped_images']} existing)"
        )

    # Load model versions
    model_versions_file = seeds_dir / "model_versions.json"
    if model_versions_file.exists():
        print(f"Loading model versions from {model_versions_file}...")
        with open(model_versions_file) as f:
            model_versions_data = json.load(f)

        for model_data in model_versions_data:
            # Check if model version already exists
            existing = session.exec(
                select(ModelVersion).where(ModelVersion.id == model_data["id"])
            ).first()

            if existing:
                stats["skipped_model_versions"] += 1
                continue

            model_version = ModelVersion(
                id=model_data["id"],
                name=model_data["name"],
                description=model_data.get("description"),
                artifact_path=model_data.get("artifact_path"),
            )
            session.add(model_version)
            stats["model_versions"] += 1

        session.commit()
        print(
            f"  ✓ Loaded {stats['model_versions']} model versions (skipped {stats['skipped_model_versions']} existing)"
        )

    # Load predicted labels
    predicted_labels_file = seeds_dir / "predicted_labels.json"
    if predicted_labels_file.exists():
        print(f"Loading predicted labels from {predicted_labels_file}...")
        with open(predicted_labels_file) as f:
            predicted_labels_data = json.load(f)

        # Get pathology ID mapping
        pathology_map: dict[str, int] = {}
        for pathology in session.exec(select(Pathology)).all():
            if pathology.id is not None:
                pathology_map[pathology.code] = pathology.id

        for idx, pred_data in enumerate(predicted_labels_data, 1):
            pathology_id: int | None = pathology_map.get(pred_data["pathology_code"])
            if not pathology_id:
                print(f"  ⚠️  Unknown pathology code: {pred_data['pathology_code']}")
                continue

            # Check if this prediction already exists
            existing = session.exec(
                select(ImagePredictedLabel).where(
                    ImagePredictedLabel.image_id == pred_data["image_id"],
                    ImagePredictedLabel.model_version_id
                    == pred_data["model_version_id"],
                    ImagePredictedLabel.pathology_id == pathology_id,
                )
            ).first()

            if existing:
                continue

            predicted_label = ImagePredictedLabel(
                image_id=pred_data["image_id"],
                model_version_id=pred_data["model_version_id"],
                pathology_id=pathology_id,
                probability=pred_data["probability"],
                predicted_label=pred_data["predicted_label"],
            )
            session.add(predicted_label)
            stats["predicted_labels"] += 1

            # Commit in batches
            if idx % 500 == 0:
                session.commit()
                print(f"  Progress: {idx}/{len(predicted_labels_data)} predictions...")

        session.commit()
        print(f"  ✓ Loaded {stats['predicted_labels']} predicted labels")

    # Load doctor labels
    doctor_labels_file = seeds_dir / "doctor_labels.json"
    if doctor_labels_file.exists():
        print(f"Loading doctor labels from {doctor_labels_file}...")
        with open(doctor_labels_file) as f:
            doctor_labels_data = json.load(f)

        # Get pathology ID mapping
        pathology_map: dict[str, int] = {}
        for pathology in session.exec(select(Pathology)).all():
            if pathology.id is not None:
                pathology_map[pathology.code] = pathology.id

        for idx, label_data in enumerate(doctor_labels_data, 1):
            pathology_id: int | None = pathology_map.get(label_data["pathology_code"])
            if not pathology_id:
                print(f"  ⚠️  Unknown pathology code: {label_data['pathology_code']}")
                continue

            # Check if this doctor label already exists
            existing = session.exec(
                select(DoctorLabel).where(
                    DoctorLabel.image_id == label_data["image_id"],
                    DoctorLabel.model_version_id == label_data["model_version_id"],
                    DoctorLabel.pathology_id == pathology_id,
                    DoctorLabel.labeled_by == label_data["labeled_by"],
                )
            ).first()

            if existing:
                continue

            doctor_label = DoctorLabel(
                image_id=label_data["image_id"],
                model_version_id=label_data["model_version_id"],
                pathology_id=pathology_id,
                is_present=label_data["is_present"],
                comment=label_data.get("comment"),
                labeled_by=label_data["labeled_by"],
            )
            session.add(doctor_label)
            stats["doctor_labels"] += 1

            # Commit in batches
            if idx % 500 == 0:
                session.commit()
                print(f"  Progress: {idx}/{len(doctor_labels_data)} labels...")

        session.commit()
        print(f"  ✓ Loaded {stats['doctor_labels']} doctor labels")

    return stats
