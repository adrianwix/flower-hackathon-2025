#!/usr/bin/env python3
"""
Database initialization script.

This script creates all database tables and seeds initial data.
"""

from pathlib import Path

from database import create_db_and_tables, init_pathologies
from dependencies import get_session
from seed_loader import load_seed_data
from models import User, UserRole
from sqlmodel import Session, select


def init_default_user(session: Session) -> None:
    """Create a default doctor user for seed data labels"""
    existing = session.exec(select(User).where(User.id == 1)).first()
    if not existing:
        default_user = User(
            id=1,
            email="seed.doctor@example.com",
            full_name="Seed Data Doctor",
            password_hash="dummy_hash_for_seed_data",
            role=UserRole.DOCTOR.value,
        )
        session.add(default_user)
        session.commit()
        print("✓ Default user created (ID: 1)")
    else:
        print("✓ Default user already exists")


def main():
    """Initialize the database"""
    print("Creating database tables...")
    create_db_and_tables()
    print("✓ Tables created successfully")

    print("\nInitializing pathologies...")
    session = next(get_session())
    init_pathologies(session)
    print("✓ Pathologies initialized")

    print("\nInitializing default user...")
    init_default_user(session)

    # Load seed data if available
    seeds_dir = Path(__file__).parent / "seeds"
    if seeds_dir.exists():
        print(f"\nLoading seed data from {seeds_dir}...")
        stats = load_seed_data(session, seeds_dir)
        print("\n✓ Seed data loaded successfully:")
        print(
            f"  - Patients: {stats['patients']} loaded, {stats['skipped_patients']} skipped"
        )
        print(f"  - Exams: {stats['exams']} loaded, {stats['skipped_exams']} skipped")
        print(
            f"  - Images: {stats['images']} loaded, {stats['skipped_images']} skipped"
        )
        print(
            f"  - Model versions: {stats['model_versions']} loaded, {stats['skipped_model_versions']} skipped"
        )
        print(f"  - Predicted labels: {stats['predicted_labels']} loaded")
        print(f"  - Doctor labels: {stats['doctor_labels']} loaded")
    else:
        print(f"\n⚠️  No seed data found at {seeds_dir}")

    print("\nDatabase initialization complete!")


if __name__ == "__main__":
    main()
