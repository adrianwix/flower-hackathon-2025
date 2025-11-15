#!/usr/bin/env python3
"""
Find all possible labels in Data_Entry_2017.csv from the NIH Chest X-ray dataset.

This script:
1. Reads the Data_Entry_2017.csv file
2. Extracts all unique labels from the "Finding Labels" column
3. Counts occurrences of each label
4. Displays results sorted by frequency
"""

import pandas as pd
from collections import Counter
from pathlib import Path


def find_all_labels(csv_path: Path):
    """Find and count all unique labels in the dataset"""
    print(f"Reading {csv_path}...")

    # Read the CSV file
    df = pd.read_csv(csv_path)

    print(f"Total records: {len(df):,}")
    print(f"\nExtracting labels from 'Finding Labels' column...\n")

    # Counter for all labels
    label_counter = Counter()

    # Process each row's Finding Labels
    for finding_labels in df["Finding Labels"]:
        if pd.notna(finding_labels):
            # Split by pipe character and count each label
            labels = [label.strip() for label in str(finding_labels).split("|")]
            label_counter.update(labels)

    # Display results
    print("=" * 70)
    print(f"{'Label':<25} {'Count':>12} {'Percentage':>12}")
    print("=" * 70)

    total_occurrences = sum(label_counter.values())

    for label, count in label_counter.most_common():
        percentage = (count / len(df)) * 100
        print(f"{label:<25} {count:>12,} {percentage:>11.2f}%")

    print("=" * 70)
    print(f"Total unique labels: {len(label_counter)}")
    print(f"Total label occurrences: {total_occurrences:,}")
    print(f"Total images: {len(df):,}")
    print(f"Average labels per image: {total_occurrences / len(df):.2f}")

    # Return the list of unique labels
    return sorted(label_counter.keys())


def main():
    """Main execution"""
    # Path to the CSV file
    csv_path = Path(__file__).parent / "nih_chest_x_rays" / "Data_Entry_2017.csv"

    if not csv_path.exists():
        print(f"Error: File not found: {csv_path}")
        return 1

    # Find all labels
    unique_labels = find_all_labels(csv_path)

    # Print the list for easy copying
    print("\n" + "=" * 70)
    print("UNIQUE LABELS (sorted alphabetically):")
    print("=" * 70)
    for label in unique_labels:
        print(f"  - {label}")

    # Print as Python list
    print("\n" + "=" * 70)
    print("As Python list:")
    print("=" * 70)
    print(unique_labels)

    return 0


if __name__ == "__main__":
    exit(main())
