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

        # Reopen for format check (verify closes the file)
        img = Image.open(io.BytesIO(image_bytes))

        # Check image format
        if img.format not in ["PNG", "JPEG", "JPG", "DICOM"]:
            return False, f"Unsupported image format: {img.format}"

        return True, ""
    except Exception as e:
        return False, f"Invalid image: {str(e)}"


def preprocess_image_for_multilabel(image_bytes: bytes) -> torch.Tensor:
    """
    Preprocess image for torchxrayvision model.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Preprocessed image tensor (1, 1, 224, 224)
    """
    # Load image
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_array = np.array(img)

    # Convert to grayscale
    if len(img_array.shape) == 3:
        img_array = img_array.mean(axis=2)

    # Normalize to [0, 1]
    img_array = img_array / 255.0

    # Resize to 224x224
    img_resized = Image.fromarray((img_array * 255).astype(np.uint8)).resize((224, 224))
    img_array = np.array(img_resized) / 255.0

    # Add channel and batch dimensions
    img_tensor = torch.from_numpy(img_array).unsqueeze(0).unsqueeze(0).float()  # pyright: ignore[reportUnknownMemberType]

    return img_tensor


def preprocess_image_for_binary(image_bytes: bytes) -> torch.Tensor:
    """
    Preprocess image for binary classification model.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Preprocessed image tensor (1, 1, 224, 224)
    """
    # Load and convert to grayscale
    img = Image.open(io.BytesIO(image_bytes)).convert("L")
    img_resized = img.resize((224, 224))
    img_array = np.array(img_resized) / 255.0

    # Keep as single-channel (ResNet modified to accept 1 channel)
    img_array = np.expand_dims(img_array, axis=0)

    # Convert to tensor and add batch dimension
    img_tensor = torch.from_numpy(img_array).unsqueeze(0).float()  # pyright: ignore[reportUnknownMemberType]

    return img_tensor


def preprocess_image(image_bytes: bytes) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Preprocess the X-ray image for both models.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Tuple of (multilabel_tensor, binary_tensor)
    """
    multilabel_tensor = preprocess_image_for_multilabel(image_bytes)
    binary_tensor = preprocess_image_for_binary(image_bytes)

    return multilabel_tensor, binary_tensor
