"""
X-ray pathology detection models.

Combines two models:
1. torchxrayvision DenseNet121 for multi-label pathology classification
2. Custom ResNet18 for binary Finding/No Finding classification
"""

from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import torch
import torch.nn as nn
import torchvision.models as models  # type: ignore
import torchxrayvision as xrv  # type: ignore
from PIL import Image as PILImage


class DualXRayModel:
    """
    Dual model for X-ray analysis:
    - Multi-label pathology detection (torchxrayvision)
    - Binary finding detection (custom ResNet18)
    """

    def __init__(
        self,
        binary_model_path: str = "ml/models/version1_job1124_resnet18_FedProx6Rounds_round6_auroc7288.pt",
    ):
        """
        Initialize both models.

        Args:
            binary_model_path: Path to the binary classification model weights
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load torchxrayvision model for multi-label classification
        print("Loading torchxrayvision DenseNet121...")
        self.multilabel_model = xrv.models.DenseNet(weights="densenet121-res224-all")
        self.multilabel_model = self.multilabel_model.to(self.device)
        self.multilabel_model.eval()
        self.multilabel_pathologies: list[str] = self.multilabel_model.pathologies  # type: ignore

        # Load custom ResNet18 for binary classification
        print(f"Loading binary classification ResNet18 from {binary_model_path}...")
        self.binary_model = self._load_binary_model(binary_model_path)
        self.binary_model = self.binary_model.to(self.device)
        self.binary_model.eval()

        print(f"Initialized DualXRayModel on {self.device}")

    def _load_binary_model(self, model_path: str) -> nn.Module:
        """
        Load the binary classification ResNet18 model.

        Args:
            model_path: Path to model weights

        Returns:
            Loaded PyTorch model
        """
        # Create ResNet18 architecture with single output (binary classification)
        model = models.resnet18(weights=None)
        # Modify first conv layer for grayscale input (1 channel instead of 3)
        model.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        model.fc = nn.Linear(model.fc.in_features, 1)  # Binary output

        # Load trained weights
        full_path = Path(__file__).parent.parent / model_path
        if not full_path.exists():
            raise FileNotFoundError(f"Binary model not found at {full_path}")

        checkpoint = torch.load(full_path, map_location=self.device)
        # Fix: Strip 'model.' prefix from checkpoint keys if present
        if any(k.startswith("model.") for k in checkpoint.keys()):
            checkpoint = {k.replace("model.", ""): v for k, v in checkpoint.items()}
        # Load state dict (checkpoint was saved for a 1-channel conv1 in some cases)
        model.load_state_dict(checkpoint)

        return model

    def _preprocess_image_for_multilabel(self, image_path: Path) -> torch.Tensor:
        """
        Preprocess image for torchxrayvision model.

        Args:
            image_path: Path to the image file

        Returns:
            Preprocessed image tensor
        """
        # Load image
        img = PILImage.open(image_path).convert("RGB")
        img_array = np.array(img)

        # Convert to grayscale
        if len(img_array.shape) == 3:
            img_array = img_array.mean(axis=2)

        # Normalize to [0, 1]
        img_array = img_array / 255.0

        # Resize to 224x224
        img_resized = PILImage.fromarray((img_array * 255).astype(np.uint8)).resize(
            (224, 224)
        )
        img_array = np.array(img_resized) / 255.0

        # Add channel and batch dimensions
        img_tensor = torch.from_numpy(img_array).unsqueeze(0).unsqueeze(0).float()  # type: ignore

        return img_tensor.to(self.device)

    def _preprocess_image_for_binary(self, image_path: Path) -> torch.Tensor:
        """
        Preprocess image for binary classification model.

        Args:
            image_path: Path to the image file

        Returns:
            Preprocessed image tensor
        """
        # Load and convert to grayscale
        img = PILImage.open(image_path).convert("L")
        img_resized = img.resize((224, 224))
        img_array = np.array(img_resized) / 255.0

        # Keep as single-channel (ResNet modified to accept 1 channel)
        img_array = np.expand_dims(img_array, axis=0)

        # Convert to tensor and add batch dimension
        img_tensor = torch.from_numpy(img_array).unsqueeze(0).float()  # type: ignore

        return img_tensor.to(self.device)

    def predict_multilabel(
        self, img_tensor: torch.Tensor, threshold: float = 0.5
    ) -> Dict[str, Dict[str, object]]:
        """
        Predict multiple pathology labels using torchxrayvision.

        Args:
            img_tensor: Preprocessed image tensor (1, 1, 224, 224)
            threshold: Probability threshold for positive predictions

        Returns:
            Dictionary of {pathology_code: (predicted_label, probability)}
        """
        img_tensor = img_tensor.to(self.device)

        with torch.no_grad():
            outputs = self.multilabel_model(img_tensor)
            probabilities = torch.sigmoid(outputs).cpu().numpy()[0]

        results: Dict[str, Dict[str, object]] = {}
        for pathology, probability in zip(self.multilabel_pathologies, probabilities):
            predicted_label = probability > threshold
            results[pathology] = {
                "predicted_label": bool(predicted_label),
                "probability": float(probability),
            }

        return results

    def predict_binary(
        self, img_tensor: torch.Tensor, threshold: float = 0.5
    ) -> Tuple[str, float, bool]:
        """
        Predict binary Finding/No Finding using custom ResNet18.

        Args:
            img_tensor: Preprocessed image tensor (1, 1, 224, 224)
            threshold: Probability threshold for positive prediction

        Returns:
            Tuple of (label, probability, predicted_label)
            where label is "Finding" or "No Finding"
        """
        img_tensor = img_tensor.to(self.device)

        with torch.no_grad():
            output = self.binary_model(img_tensor)
            probability = torch.sigmoid(output).item()

        has_finding = probability >= threshold
        label = "Finding" if has_finding else "No Finding"

        return label, float(probability), bool(has_finding)

    def predict_all(
        self,
        multilabel_tensor: torch.Tensor,
        binary_tensor: torch.Tensor,
        threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Run both binary and multi-label predictions.

        Args:
            multilabel_tensor: Preprocessed tensor for multilabel model (1, 1, 224, 224)
            binary_tensor: Preprocessed tensor for binary model (1, 1, 224, 224)
            threshold: Probability threshold for positive predictions

        Returns:
            Dictionary with both binary and multi-label predictions
        """
        # Binary prediction (Finding vs No Finding)
        binary_label, binary_prob, has_finding = self.predict_binary(
            binary_tensor, threshold
        )

        # Multi-label predictions
        multilabel_predictions = self.predict_multilabel(multilabel_tensor, threshold)

        return {
            "binary_prediction": {
                "label": binary_label,
                "probability": binary_prob,
                "has_finding": has_finding,
            },
            "multi_label_predictions": multilabel_predictions,
            "threshold": threshold,
        }


# Singleton instance
_model_instance = None


def get_model() -> DualXRayModel:
    """
    Get or create the singleton model instance.

    Returns:
        DualXRayModel instance
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = DualXRayModel()
    return _model_instance
