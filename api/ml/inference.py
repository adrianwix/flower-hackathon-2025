"""
Inference pipeline for X-ray pathology detection.
"""

from typing import Any, Dict

from ml.model import get_model
from ml.preprocessing import preprocess_image


async def predict_image(
    image_bytes: bytes,
    threshold: float = 0.5,
) -> Dict[str, Any]:
    """
    Predict pathologies for an X-ray image.

    Args:
        image_bytes: Raw image bytes
        threshold: Probability threshold

    Returns:
        Prediction results
    """
    # Preprocess image for both models
    multilabel_tensor, binary_tensor = preprocess_image(image_bytes)

    # Get model and run prediction
    model = get_model()
    predictions = model.predict_all(multilabel_tensor, binary_tensor, threshold)

    return predictions
