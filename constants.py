"""
Application constants and shared configuration.

Single source of truth for pathology labels and other constants.
This file is shared between the root scripts and the api module.
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
