"""
Pytest configuration and fixtures.
"""

import io
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from PIL import Image as PILImage
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app
from dependencies import get_session
from database import init_pathologies


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Initialize pathologies
        init_pathologies(session)
        session.commit()
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> TestClient:
    """
    Create a test client with overridden dependencies.
    """

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_xray_bytes() -> bytes:
    """
    Create a sample X-ray image as bytes.
    """
    # Create a simple grayscale image
    img = PILImage.new("L", (224, 224), color=128)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes.read()


@pytest.fixture
def sample_patient_data() -> dict:
    """
    Sample patient data for testing.
    """
    return {
        "first_name": "John",
        "last_name": "Doe",
        "birth_year": 1980,
        "sex": "M",
    }
