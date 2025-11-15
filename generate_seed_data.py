#!/usr/bin/env python3
"""
Generate a representative subset of 500 patients from the NIH Chest X-ray dataset.

This script:
1. Analyzes the full dataset to understand finding distributions
2. Selects 500 representative patients using stratified sampling
3. Generates ML predictions using:
   - torchxrayvision DenseNet121 for multi-label classification
   - Custom ResNet18 for binary Finding/No Finding classification
4. Creates doctor labels from ground truth Finding Labels
5. Copies their images and creates seed JSON files for database initialization
"""

import json
import random
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Set, List, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torchvision.models as models
import torchxrayvision as xrv
from faker import Faker
from PIL import Image as PILImage


def analyze_dataset(df: pd.DataFrame) -> Dict:
    """Analyze the dataset to understand patient and finding distributions"""
    print("\n📊 Analyzing dataset...")

    # Basic stats
    total_images = len(df)
    total_patients = df["Patient ID"].nunique()

    print(f"  Total images: {total_images:,}")
    print(f"  Total unique patients: {total_patients:,}")
    print(f"  Average images per patient: {total_images / total_patients:.2f}")

    # Finding distribution
    finding_counter = Counter()
    for findings in df["Finding Labels"]:
        if pd.notna(findings):
            for finding in findings.split("|"):
                finding_counter[finding.strip()] += 1

    print("\n  Finding distribution:")
    for finding, count in finding_counter.most_common():
        pct = (count / total_images) * 100
        print(f"    {finding:20s}: {count:6,} ({pct:5.2f}%)")

    return {
        "total_images": total_images,
        "total_patients": total_patients,
        "finding_distribution": finding_counter,
        "finding_percentages": {
            finding: (count / total_images) * 100
            for finding, count in finding_counter.items()
        },
    }


def get_patient_finding_profile(patient_df: pd.DataFrame) -> Set[str]:
    """Get all unique findings for a patient across all their images"""
    findings = set()
    for finding_labels in patient_df["Finding Labels"]:
        if pd.notna(finding_labels):
            for finding in finding_labels.split("|"):
                findings.add(finding.strip())
    return findings


def stratified_patient_selection(
    df: pd.DataFrame,
    source_images_dir: Path,
    target_count: int = 500,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Select patients using stratified sampling to maintain finding distributions.
    Only select patients whose images are actually available on disk.

    Strategy:
    1. Filter to patients with available images
    2. Group patients by their finding profiles (combination of findings)
    3. Sample proportionally from each group
    4. Ensure we maintain the overall distribution
    """
    print(f"\n🎯 Selecting {target_count} representative patients...")

    # First, filter to only patients whose images are available
    print("  Checking image availability...")
    available_images = set()
    for subdir in source_images_dir.glob("images_*"):
        img_dir = subdir / "images"
        if img_dir.exists():
            available_images.update(f.name for f in img_dir.iterdir() if f.is_file())

    print(f"  Found {len(available_images):,} available images")

    # Filter dataframe to only available images
    df = df[df["Image Index"].isin(available_images)].copy()
    print(f"  Filtered to {len(df):,} records with available images")
    print(f"  From {df['Patient ID'].nunique():,} patients")

    # Continue with stratified selection
    print("\n  Performing stratified selection...")

    # Create patient profiles
    patient_profiles = []
    for patient_id in df["Patient ID"].unique():
        patient_data = df[df["Patient ID"] == patient_id]
        findings = get_patient_finding_profile(patient_data)

        # Create a sortable string representation of findings
        finding_key = "|".join(sorted(findings))

        patient_profiles.append(
            {
                "patient_id": patient_id,
                "finding_key": finding_key,
                "findings": findings,
                "num_images": len(patient_data),
            }
        )

    profiles_df = pd.DataFrame(patient_profiles)

    # Count profile distribution
    profile_counts = profiles_df["finding_key"].value_counts()
    print(f"  Unique finding profiles: {len(profile_counts)}")

    # For profiles with many patients, sample proportionally
    # For rare profiles, ensure we get at least some representation
    selected_patients = []

    # Calculate target samples per profile (proportional)
    total_patients = len(profiles_df)
    for finding_key, count in profile_counts.items():
        proportion = count / total_patients
        target_for_profile = max(1, int(target_count * proportion))

        # Get patients with this profile
        profile_patients = profiles_df[profiles_df["finding_key"] == finding_key]

        # Sample (with replacement if necessary, but unlikely)
        n_to_sample = min(target_for_profile, len(profile_patients))
        sampled = profile_patients.sample(n=n_to_sample, random_state=random_state)
        selected_patients.extend(sampled["patient_id"].tolist())

    # If we have too many, randomly remove some
    if len(selected_patients) > target_count:
        pd_series = pd.Series(selected_patients)
        selected_patients = pd_series.sample(
            n=target_count, random_state=random_state
        ).tolist()

    # If we have too few (rare), add random patients
    while len(selected_patients) < target_count:
        remaining = profiles_df[~profiles_df["patient_id"].isin(selected_patients)]
        if len(remaining) == 0:
            break
        additional = remaining.sample(n=1, random_state=random_state)
        selected_patients.extend(additional["patient_id"].tolist())

    print(f"  Selected {len(selected_patients)} patients")

    # Filter original dataframe to selected patients
    subset_df = df[df["Patient ID"].isin(selected_patients)].copy()

    return subset_df


def validate_subset_distribution(original_stats: Dict, subset_df: pd.DataFrame):
    """Compare the subset distribution with the original"""
    print("\n✅ Validating subset distribution...")

    subset_images = len(subset_df)
    subset_patients = subset_df["Patient ID"].nunique()

    print(f"  Subset images: {subset_images:,}")
    print(f"  Subset patients: {subset_patients:,}")
    print(f"  Average images per patient: {subset_images / subset_patients:.2f}")

    # Finding distribution in subset
    subset_finding_counter = Counter()
    for findings in subset_df["Finding Labels"]:
        if pd.notna(findings):
            for finding in findings.split("|"):
                subset_finding_counter[finding.strip()] += 1

    print("\n  Finding distribution comparison:")
    print(f"  {'Finding':20s} {'Original %':>12s} {'Subset %':>12s} {'Diff':>8s}")
    print("  " + "-" * 56)

    for finding in original_stats["finding_distribution"].keys():
        original_pct = original_stats["finding_percentages"][finding]
        subset_pct = (subset_finding_counter[finding] / subset_images) * 100
        diff = subset_pct - original_pct
        print(
            f"  {finding:20s} {original_pct:11.2f}% {subset_pct:11.2f}% {diff:+7.2f}%"
        )


def copy_images_and_create_seeds(
    subset_df: pd.DataFrame, source_images_dir: Path, output_seeds_dir: Path
) -> None:
    """
    Copy selected images and create JSON seed files for database initialization.

    Creates:
    - /api/seeds/images/ - Contains the actual image files
    - /api/seeds/patients.json - Patient data
    - /api/seeds/exams.json - Exam data with image references
    - /api/seeds/model_versions.json - Model version information
    - /api/seeds/predicted_labels.json - ML predictions for each image
    - /api/seeds/doctor_labels.json - Doctor labels from ground truth
    """
    print(f"\n📦 Creating seed data in {output_seeds_dir}...")

    # Create output directories
    images_dir = output_seeds_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # Initialize ML models
    print("\n🤖 Loading ML models...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"  Using device: {device}")

    # Load torchxrayvision DenseNet model for multi-label classification
    print("  Loading torchxrayvision DenseNet121...")
    multilabel_model = xrv.models.DenseNet(weights="densenet121-res224-all")
    multilabel_model = multilabel_model.to(device)
    multilabel_model.eval()
    model_pathologies = multilabel_model.pathologies
    print(f"  ✓ Multi-label model loaded with {len(model_pathologies)} pathologies")

    # Load custom ResNet18 for binary classification
    print("  Loading binary classification ResNet18...")
    binary_model = models.resnet18(weights=None)
    # Modify first conv layer for grayscale input (1 channel instead of 3)
    binary_model.conv1 = nn.Conv2d(
        1, 64, kernel_size=7, stride=2, padding=3, bias=False
    )
    binary_model.fc = nn.Linear(binary_model.fc.in_features, 1)  # Binary output

    binary_model_path = (
        Path(__file__).parent
        / "api"
        / "ml"
        / "models"
        / "version1_job1124_resnet18_FedProx6Rounds_round6_auroc7288.pt"
    )
    if not binary_model_path.exists():
        raise FileNotFoundError(f"Binary model not found at {binary_model_path}")

    checkpoint = torch.load(binary_model_path, map_location=device)
    # Remove 'model.' prefix from state dict keys if present
    state_dict = {k.replace("model.", ""): v for k, v in checkpoint.items()}
    binary_model.load_state_dict(state_dict)
    binary_model = binary_model.to(device)
    binary_model.eval()
    print("  ✓ Binary classification model loaded")

    print(f"\n  Model pathologies:")
    for i, pathology in enumerate(model_pathologies):
        print(f"    {i}: {pathology}")

    # Initialize Faker for generating names
    fake = Faker()
    Faker.seed(42)  # Set seed for reproducibility

    # Set random seed for reproducibility (for reviewed_at field)
    random.seed(42)

    # Data structures for JSON
    patients_data = []
    exams_data = []
    images_data = []
    predicted_labels_data = []
    doctor_labels_data = []

    # Model version records
    model_versions_data = [
        {
            "id": 1,
            "name": "torchxrayvision_densenet121_res224_all",
            "description": "DenseNet121 trained on multiple chest X-ray datasets (res224-all weights) for multi-label classification",
            "artifact_path": "torchxrayvision://densenet121-res224-all",
        },
        {
            "id": 2,
            "name": "resnet18_fedprox_round6",
            "description": "ResNet18 trained with FedProx for 6 rounds (AUROC 72.88%) for binary Finding/No Finding classification",
            "artifact_path": "ml/models/version1_job1124_resnet18_FedProx6Rounds_round6_auroc7288.pt",
        },
    ]

    # Track progress
    copied_count = 0
    missing_count = 0
    prediction_count = 0

    # Process by patient
    patient_ids = subset_df["Patient ID"].unique()

    for patient_idx, patient_id in enumerate(patient_ids, 1):
        patient_df = subset_df[subset_df["Patient ID"] == patient_id].sort_values(
            "Follow-up #"
        )

        # Create patient record
        first_record = patient_df.iloc[0]

        # Calculate birth year from patient age (assuming it is 2025)
        current_year = 2025
        patient_age = first_record["Patient Age"]
        birth_year = None
        if pd.notna(patient_age):
            birth_year = current_year - int(patient_age)

        # Get patient gender
        patient_gender = (
            str(first_record["Patient Gender"])
            if pd.notna(first_record["Patient Gender"])
            else None
        )

        # Generate fake names based on gender
        first_name = None
        last_name = None
        if patient_gender:
            if patient_gender.upper() == "M":
                first_name = fake.first_name_male()
            elif patient_gender.upper() == "F":
                first_name = fake.first_name_female()
            else:
                first_name = fake.first_name()
            last_name = fake.last_name()

        patient_data = {
            "id": int(patient_id),
            "external_patient_id": f"NIH_{patient_id}",
            "first_name": first_name,
            "last_name": last_name,
            "birth_year": birth_year,
            "sex": patient_gender,
        }
        patients_data.append(patient_data)

        # Create exam record (one per patient, grouping all their images)
        exam_id = int(patient_id)  # Use patient_id as exam_id for simplicity
        exam_data = {
            "id": exam_id,
            "patient_id": int(patient_id),
            "exam_datetime": None,  # Will be set during DB init
            "reason": "NIH Chest X-ray dataset - Follow-up series",
            "created_by": None,
        }
        exams_data.append(exam_data)

        # Process each image for this patient
        for _, row in patient_df.iterrows():
            image_filename = row["Image Index"]

            # Find the source image (checking images_001, images_002, etc.)
            source_path = None
            for subdir in source_images_dir.glob("images_*"):
                candidate = subdir / "images" / image_filename
                if candidate.exists():
                    source_path = candidate
                    break

            if source_path and source_path.exists():
                # Load, preprocess, and save image as grayscale 224x224
                img = PILImage.open(source_path).convert("L")  # Convert to grayscale
                img_resized = img.resize((224, 224))  # Resize to 224x224

                dest_path = images_dir / image_filename
                img_resized.save(dest_path)
                copied_count += 1

                # Parse ground truth findings
                finding_labels = []
                if pd.notna(row["Finding Labels"]):
                    raw_findings = row["Finding Labels"].split("|")
                    finding_labels = [f.strip() for f in raw_findings]

                # Assign image_id before predictions to avoid UnboundLocalError
                image_id = len(images_data) + 1  # Auto-increment ID

                # Generate ML predictions
                try:
                    # Multi-label predictions from torchxrayvision
                    multilabel_predictions = generate_multilabel_predictions(
                        source_path, multilabel_model, device, model_pathologies
                    )

                    # Binary prediction from custom ResNet18
                    binary_prediction = generate_binary_prediction(
                        source_path, binary_model, device
                    )

                    # Store multi-label predictions (model_version_id=1)
                    for pathology, probability in multilabel_predictions:
                        # Use 0.5 threshold for binary prediction
                        predicted_label = probability > 0.5

                        predicted_labels_data.append(
                            {
                                "image_id": image_id,
                                "model_version_id": 1,
                                "pathology_code": pathology,
                                "probability": float(probability),
                                "predicted_label": bool(predicted_label),
                            }
                        )
                        prediction_count += 1

                    # Store binary prediction (model_version_id=2)
                    binary_label, binary_prob, has_finding = binary_prediction
                    predicted_labels_data.append(
                        {
                            "image_id": image_id,
                            "model_version_id": 2,
                            "pathology_code": binary_label,
                            "probability": float(binary_prob),
                            "predicted_label": bool(has_finding),
                        }
                    )
                    prediction_count += 1

                    # Create doctor labels from ground truth
                    # For "No Finding" case
                    if "No Finding" in finding_labels:
                        doctor_labels_data.append(
                            {
                                "image_id": image_id,
                                "model_version_id": 1,
                                "pathology_code": "No Finding",
                                "is_present": True,
                                "comment": "Ground truth from NIH dataset",
                                "labeled_by": 1,  # Default doctor user ID
                            }
                        )
                    else:
                        # For each pathology in ground truth, create a doctor label
                        for pathology_code in finding_labels:
                            if pathology_code != "No Finding":
                                doctor_labels_data.append(
                                    {
                                        "image_id": image_id,
                                        "model_version_id": 1,
                                        "pathology_code": pathology_code,
                                        "is_present": True,
                                        "comment": "Ground truth from NIH dataset",
                                        "labeled_by": 1,  # Default doctor user ID
                                    }
                                )

                except Exception as e:
                    print(
                        f"  ⚠️  Failed to generate predictions for {image_filename}: {e}"
                    )

                # Create image record
                # 95% of images should be marked as reviewed (only 5% need review)
                reviewed_at = None
                if random.random() < 0.95:
                    # Generate a random reviewed timestamp within the past 30 days
                    days_ago = random.randint(1, 30)
                    hours_ago = random.randint(0, 23)
                    reviewed_at = (
                        datetime.now(timezone.utc)
                        - timedelta(days=days_ago, hours=hours_ago)
                    ).isoformat()

                image_data = {
                    "id": image_id,
                    "exam_id": exam_id,
                    "filename": image_filename,
                    "view_position": str(row["View Position"])
                    if pd.notna(row["View Position"])
                    else None,
                    "follow_up_number": int(row["Follow-up #"])
                    if pd.notna(row["Follow-up #"])
                    else 0,
                    "reviewed_at": reviewed_at,
                }
                images_data.append(image_data)
            else:
                missing_count += 1
                print(f"  ⚠️  Missing image: {image_filename}")

        # Progress update
        if patient_idx % 50 == 0:
            print(f"  Processed {patient_idx}/{len(patient_ids)} patients...")

    print(f"\n  ✓ Copied {copied_count} images")
    print(f"  ✓ Generated {prediction_count} ML predictions")
    print(f"  ✓ Created {len(doctor_labels_data)} doctor labels from ground truth")
    if missing_count > 0:
        print(f"  ⚠️  Missing {missing_count} images")

    # Write JSON files
    with open(output_seeds_dir / "patients.json", "w") as f:
        json.dump(patients_data, f, indent=2)

    with open(output_seeds_dir / "exams.json", "w") as f:
        json.dump(exams_data, f, indent=2)

    with open(output_seeds_dir / "images.json", "w") as f:
        json.dump(images_data, f, indent=2)

    with open(output_seeds_dir / "model_versions.json", "w") as f:
        json.dump(model_versions_data, f, indent=2)

    with open(output_seeds_dir / "predicted_labels.json", "w") as f:
        json.dump(predicted_labels_data, f, indent=2)

    with open(output_seeds_dir / "doctor_labels.json", "w") as f:
        json.dump(doctor_labels_data, f, indent=2)

    # Write summary
    summary = {
        "total_patients": len(patients_data),
        "total_exams": len(exams_data),
        "total_images": len(images_data),
        "images_copied": copied_count,
        "images_missing": missing_count,
        "ml_predictions": prediction_count,
        "doctor_labels": len(doctor_labels_data),
        "model_versions": [mv["name"] for mv in model_versions_data],
    }

    with open(output_seeds_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n  ✓ Created patients.json ({len(patients_data)} patients)")
    print(f"  ✓ Created exams.json ({len(exams_data)} exams)")
    print(f"  ✓ Created images.json ({len(images_data)} images)")
    print("  ✓ Created model_versions.json (1 model)")
    print(f"  ✓ Created predicted_labels.json ({prediction_count} predictions)")
    print(f"  ✓ Created doctor_labels.json ({len(doctor_labels_data)} labels)")
    print("  ✓ Created summary.json")


def generate_multilabel_predictions(
    image_path: Path, model, device, pathologies: List[str]
) -> List[Tuple[str, float]]:
    """
    Generate multi-label predictions for a single image using torchxrayvision model.

    Returns:
        List of tuples (pathology_name, probability)
    """
    # Load and preprocess image
    img = PILImage.open(image_path).convert("L")  # Convert to grayscale

    # Resize to 224x224 (model input size)
    img = img.resize((224, 224))

    # Convert to numpy array
    img_array = np.array(img)

    # Normalize to [-1024, 1024] range as expected by torchxrayvision
    # Assuming input is in [0, 255] range, scale to approximate [-1024, 1024]
    img_array = (img_array / 255.0) * 2048 - 1024

    # Add channel dimension and convert to torch tensor
    img_tensor = torch.from_numpy(img_array).unsqueeze(0).float()

    # Add batch dimension
    img_tensor = img_tensor.unsqueeze(0).to(device)

    # Generate predictions
    with torch.no_grad():
        outputs = model(img_tensor)

    # Convert to probabilities using sigmoid
    probabilities = torch.sigmoid(outputs).cpu().numpy()[0]

    # Return list of (pathology, probability) tuples
    return list(zip(pathologies, probabilities))


def generate_binary_prediction(
    image_path: Path, model: nn.Module, device: torch.device
) -> Tuple[str, float, bool]:
    """
    Generate binary Finding/No Finding prediction using custom ResNet18.

    Args:
        image_path: Path to the image file
        model: Custom ResNet18 model
        device: torch device (cuda/cpu)

    Returns:
        Tuple of (label, probability, has_finding)
    """
    # Load and preprocess image
    img = PILImage.open(image_path).convert("L")  # Convert to grayscale
    img = img.resize((224, 224))
    img_array = np.array(img)

    # Normalize to [0, 1]
    img_array = img_array / 255.0

    # Add channel dimension (grayscale = 1 channel)
    img_array = np.expand_dims(img_array, axis=0)

    # Convert to tensor
    img_tensor = torch.from_numpy(img_array).float()

    # Move to device and add batch dimension
    img_tensor = img_tensor.to(device).unsqueeze(0)

    # Get prediction
    model.eval()
    with torch.no_grad():
        output = model(img_tensor)
        # Apply sigmoid to get probability
        prob = torch.sigmoid(output).cpu().item()

    # Determine label based on probability
    has_finding = prob > 0.5
    label = "Finding" if has_finding else "No Finding"

    return label, prob, has_finding


def main():
    """Main execution"""
    print("=" * 80)
    print("NIH Chest X-ray Dataset - Representative Subset Generator")
    print("=" * 80)

    # Paths
    base_dir = Path(__file__).parent
    data_csv = base_dir / "nih_chest_x_rays" / "Data_Entry_2017.csv"
    images_dir = base_dir / "nih_chest_x_rays"
    output_dir = base_dir / "api" / "seeds"

    # Validate paths
    if not data_csv.exists():
        print(f"❌ Error: Data file not found: {data_csv}")
        return 1

    if not images_dir.exists():
        print(f"❌ Error: Images directory not found: {images_dir}")
        return 1

    # Load dataset
    print(f"\n📂 Loading dataset from {data_csv}...")
    df = pd.read_csv(data_csv)
    print(f"  ✓ Loaded {len(df):,} records")

    # Analyze original dataset
    original_stats = analyze_dataset(df)

    # Select representative subset
    subset_df = stratified_patient_selection(df, images_dir, target_count=500)

    # Validate distribution
    validate_subset_distribution(original_stats, subset_df)

    # Copy images and create seed files
    copy_images_and_create_seeds(subset_df, images_dir, output_dir)

    print("\n" + "=" * 80)
    print("✅ Seed data generation complete!")
    print("=" * 80)
    print(f"\nSeed data location: {output_dir}")
    print("Next step: Update api/init_db.py to load this seed data into the database")

    return 0


if __name__ == "__main__":
    exit(main())
