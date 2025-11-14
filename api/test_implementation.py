"""
Quick test script to verify the implementation without database.

Tests:
1. Model imports
2. Enums
3. Mock model prediction
4. Image validation
"""

import io
from PIL import Image as PILImage


def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from models import (
            User,
            Patient,
            Exam,
            Image,
            Pathology,
            ModelVersion,
            ImagePredictedLabel,
            DoctorLabel,
            ReviewStatus,
            UserRole,
        )

        print("✓ models.py imports successful")
    except ImportError as e:
        print(f"✗ models.py import failed: {e}")
        return False

    try:
        from model_service import MockXRayModel, get_model, validate_image

        print("✓ model_service.py imports successful")
    except ImportError as e:
        print(f"✗ model_service.py import failed: {e}")
        return False

    return True


def test_enums():
    """Test enum definitions"""
    print("\nTesting enums...")
    try:
        from models import ReviewStatus, UserRole

        # Test ReviewStatus
        assert ReviewStatus.PENDING == "pending"
        assert ReviewStatus.IN_REVIEW == "in_review"
        assert ReviewStatus.COMPLETED == "completed"
        print("✓ ReviewStatus enum works")

        # Test UserRole
        assert UserRole.DOCTOR == "doctor"
        assert UserRole.ADMIN == "admin"
        print("✓ UserRole enum works")

        return True
    except Exception as e:
        print(f"✗ Enum test failed: {e}")
        return False


def test_mock_model():
    """Test mock model prediction"""
    print("\nTesting mock model...")
    try:
        from model_service import MockXRayModel

        # Create model instance
        model = MockXRayModel(model_version="test_v1")
        print("✓ MockXRayModel instantiated")

        # Create a simple test image
        img = PILImage.new("RGB", (100, 100), color="gray")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes = img_bytes.getvalue()
        print("✓ Test image created")

        # Test binary prediction
        has_finding, probability = model.predict_finding(img_bytes)
        assert isinstance(has_finding, bool)
        assert 0.0 <= probability <= 1.0
        print(f"✓ Binary prediction: {has_finding} (prob: {probability:.3f})")

        # Test multi-label prediction
        multi_predictions = model.predict_multi_label(img_bytes)
        assert isinstance(multi_predictions, dict)
        assert len(multi_predictions) == 14  # 14 NIH pathologies
        print(f"✓ Multi-label prediction: {len(multi_predictions)} pathologies")

        # Test predict_all
        all_predictions = model.predict_all(img_bytes)
        assert "binary_prediction" in all_predictions
        assert "multi_label_predictions" in all_predictions
        assert "model_version" in all_predictions
        assert "threshold" in all_predictions
        assert "timestamp" in all_predictions
        print("✓ predict_all works")

        return True
    except Exception as e:
        print(f"✗ Mock model test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_image_validation():
    """Test image validation"""
    print("\nTesting image validation...")
    try:
        from model_service import validate_image

        # Create valid PNG image
        img = PILImage.new("RGB", (100, 100), color="gray")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes = img_bytes.getvalue()

        is_valid, error_msg = validate_image(img_bytes)
        assert is_valid == True
        assert error_msg == ""
        print("✓ Valid PNG image accepted")

        # Test invalid data
        invalid_bytes = b"not an image"
        is_valid, error_msg = validate_image(invalid_bytes)
        assert is_valid == False
        assert len(error_msg) > 0
        print(f"✓ Invalid data rejected: {error_msg}")

        return True
    except Exception as e:
        print(f"✗ Image validation test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_model_singleton():
    """Test model singleton pattern"""
    print("\nTesting model singleton...")
    try:
        from model_service import get_model

        model1 = get_model()
        model2 = get_model()
        assert model1 is model2
        print("✓ Singleton pattern works (same instance returned)")

        return True
    except Exception as e:
        print(f"✗ Singleton test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Quick Implementation Test (No Database Required)")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Enums", test_enums()))
    results.append(("Mock Model", test_mock_model()))
    results.append(("Image Validation", test_image_validation()))
    results.append(("Model Singleton", test_model_singleton()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<50} {status}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Implementation is working correctly.")
        print("\nNext steps:")
        print("  1. Set up PostgreSQL database")
        print("  2. Run: python init_db.py")
        print("  3. Run: python example_usage.py")
        print("  4. Run: uvicorn main:app --reload")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

    return passed == total


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
