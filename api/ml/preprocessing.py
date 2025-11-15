"""
Image preprocessing for X-ray analysis.
"""

import io
from typing import Tuple

import numpy as np
import torch
from PIL import Image


def validate_image(image_bytes: bytes) -> Tuple[bool, str]:
    """
    Validate that the uploaded file is a valid image.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()

        # Check image format
        if img.format not in ["PNG", "JPEG", "JPG", "DICOM"]:
            return False, f"Unsupported image format: {img.format}"

        return True, ""
    except Exception as e:
        return False, f"Invalid image: {str(e)}"


def preprocess_image(image_bytes: bytes) -> torch.Tensor:
    """
    Preprocess the X-ray image for model input.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Preprocessed image tensor
    """
    # Load image from bytes
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # In production, apply proper preprocessing:
    # - Resize to model input size (e.g., 224x224)
    # - Normalize with ImageNet stats or dataset-specific stats
    # - Convert to tensor

    # Mock implementation: just convert to array
    img_array = np.array(img)

    # Convert to tensor (mock - in production use proper transforms)
    tensor = torch.from_numpy(img_array).float()

    return tensor
