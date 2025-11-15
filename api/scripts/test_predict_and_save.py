"""
Script to test PredictionService.predict_and_save and print debug output.
"""

from sqlmodel import Session, create_engine
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.prediction_service import PredictionService

# Adjust these as needed for your test DB and image
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"
TEST_IMAGE_ID = 1  # Change to a valid image ID in your DB


def main():
    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        service = PredictionService(session)
        import asyncio

        result = asyncio.run(service.predict_and_save(TEST_IMAGE_ID))
        print("\n[RESULT]", result)


if __name__ == "__main__":
    main()
