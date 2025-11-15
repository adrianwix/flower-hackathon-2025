"""
Application constants and shared configuration.

Single source of truth for pathology labels and other constants.
"""

# Pathology codes matching torchxrayvision model output
# These codes are used across:
# - Database (Pathology table)
# - ML model predictions
# - Seed data generation
# - API responses
PATHOLOGY_CODES = [
    "Atelectasis",
    "Cardiomegaly",
    "Consolidation",
    "Edema",
    "Effusion",
    "Emphysema",
    "Fibrosis",
    "Hernia",
    "Infiltration",
    "Mass",
    "No Finding",
    "Nodule",
    "Pleural_Thickening",
    "Pneumonia",
    "Pneumothorax",
]

# Binary classification labels
BINARY_LABELS = ["Finding", "No Finding"]

# Pathology display names and descriptions
PATHOLOGY_METADATA = {
    "Atelectasis": {
        "display_name": "Atelectasis",
        "description": "Collapse or incomplete inflation of the lung",
    },
    "Cardiomegaly": {
        "display_name": "Cardiomegaly",
        "description": "Enlargement of the heart",
    },
    "Consolidation": {
        "display_name": "Consolidation",
        "description": "Region of normally compressible lung tissue filled with liquid",
    },
    "Edema": {
        "display_name": "Edema",
        "description": "Fluid accumulation in the lungs",
    },
    "Effusion": {
        "display_name": "Effusion",
        "description": "Abnormal fluid accumulation in pleural space",
    },
    "Emphysema": {
        "display_name": "Emphysema",
        "description": "Enlargement of air spaces in the lungs",
    },
    "Fibrosis": {
        "display_name": "Fibrosis",
        "description": "Thickening and scarring of connective tissue",
    },
    "Hernia": {
        "display_name": "Hernia",
        "description": "Abnormal protrusion of tissue",
    },
    "Infiltration": {
        "display_name": "Infiltration",
        "description": "Presence of substances denser than air in lung parenchyma",
    },
    "Mass": {
        "display_name": "Mass",
        "description": "Space-occupying lesion larger than 3 cm",
    },
    "Finding": {
        "display_name": "Finding",
        "description": "Any pathology detected in the X-ray (binary classification)",
    },
    "No Finding": {
        "display_name": "No Finding",
        "description": "No pathology detected in the X-ray",
    },
    "Nodule": {
        "display_name": "Nodule",
        "description": "Space-occupying lesion less than 3 cm",
    },
    "Pleural_Thickening": {
        "display_name": "Pleural Thickening",
        "description": "Thickening of the pleura",
    },
    "Pneumonia": {
        "display_name": "Pneumonia",
        "description": "Infection of the lung",
    },
    "Pneumothorax": {
        "display_name": "Pneumothorax",
        "description": "Presence of air in the pleural space",
    },
}
