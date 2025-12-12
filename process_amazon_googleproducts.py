#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Process Amazon-GoogleProducts dataset from zip file to standard format.

This script:
1. Extracts Amazon.csv and GoogleProducts.csv
2. Converts them to tableA.csv and tableB.csv with id columns
3. Converts Amzon_GoogleProducts_perfectMapping.csv to train/valid/test.csv format
4. Then uses convert_raw_to_dataset.py to create the final dataset
"""

import pandas as pd
import os
import shutil
from pathlib import Path
import numpy as np
from sklearn.model_selection import train_test_split


# ============================================================================
# Configuration
# ============================================================================

SOURCE_ZIP_DIR = "datasets_raw/Amazon-GoogleProducts"
TEMP_DIR = "datasets_raw/Structured/Amazon-GoogleProducts"
TARGET_DATASET_NAME = "amazon_googleproducts"

# Train/valid/test split ratios
TRAIN_RATIO = 0.6
VALID_RATIO = 0.2
TEST_RATIO = 0.2

# ============================================================================


def process_amazon_googleproducts():
    """Process Amazon-GoogleProducts dataset."""
    
    # Step 1: Read the raw files
    amazon_file = Path(SOURCE_ZIP_DIR) / "Amazon.csv"
    google_file = Path(SOURCE_ZIP_DIR) / "GoogleProducts.csv"
    mapping_file = Path(SOURCE_ZIP_DIR) / "Amzon_GoogleProducts_perfectMapping.csv"
    
    if not amazon_file.exists():
        raise FileNotFoundError(f"Amazon.csv not found: {amazon_file}")
    if not google_file.exists():
        raise FileNotFoundError(f"GoogleProducts.csv not found: {google_file}")
    if not mapping_file.exists():
        raise FileNotFoundError(f"Amzon_GoogleProducts_perfectMapping.csv not found: {mapping_file}")
    
    print("Reading raw files...")
    # Try different encodings
    try:
        amazon_df = pd.read_csv(amazon_file, encoding='utf-8')
    except UnicodeDecodeError:
        amazon_df = pd.read_csv(amazon_file, encoding='latin-1')
    
    try:
        google_df = pd.read_csv(google_file, encoding='utf-8')
    except UnicodeDecodeError:
        google_df = pd.read_csv(google_file, encoding='latin-1')
    
    try:
        mapping_df = pd.read_csv(mapping_file, encoding='utf-8')
    except UnicodeDecodeError:
        mapping_df = pd.read_csv(mapping_file, encoding='latin-1')
    
    print(f"Amazon.csv: {len(amazon_df)} rows")
    print(f"GoogleProducts.csv: {len(google_df)} rows")
    print(f"Mapping file: {len(mapping_df)} matches")
    
    # Step 2: Create id columns for both tables
    # Amazon table: use existing 'id' column as key, create new numeric id
    amazon_df['original_id'] = amazon_df['id']
    amazon_df['id'] = range(len(amazon_df))
    
    # Google table: use existing 'id' column as key, create new numeric id
    google_df['original_id'] = google_df['id']
    google_df['id'] = range(len(google_df))
    
    # Create mapping dictionaries
    amazon_id_map = dict(zip(amazon_df['original_id'], amazon_df['id']))
    google_id_map = dict(zip(google_df['original_id'], google_df['id']))
    
    # Step 3: Convert mapping file to ltable_id, rtable_id format
    print("Converting mapping file...")
    matches = []
    for _, row in mapping_df.iterrows():
        amazon_id = row['idAmazon']
        google_id = row['idGoogleBase']
        
        if amazon_id in amazon_id_map and google_id in google_id_map:
            matches.append({
                'ltable_id': amazon_id_map[amazon_id],
                'rtable_id': google_id_map[google_id]
            })
        else:
            print(f"Warning: Skipping match {amazon_id} <-> {google_id} (not found in tables)")
    
    matches_df = pd.DataFrame(matches)
    print(f"Converted {len(matches_df)} valid matches")
    
    # Step 4: Create train/valid/test splits
    # Since we only have positive matches, we'll split them
    # For ZeroER, we need both positive and negative samples
    # We'll use all positive matches and generate some negative samples
    
    # Split positive matches
    train_pos, temp_pos = train_test_split(
        matches_df, 
        test_size=(VALID_RATIO + TEST_RATIO),
        random_state=42
    )
    valid_pos, test_pos = train_test_split(
        temp_pos,
        test_size=(TEST_RATIO / (VALID_RATIO + TEST_RATIO)),
        random_state=42
    )
    
    print(f"Train positive matches: {len(train_pos)}")
    print(f"Valid positive matches: {len(valid_pos)}")
    print(f"Test positive matches: {len(test_pos)}")
    
    # Generate negative samples (non-matching pairs)
    # We'll sample random pairs that are not in the matches
    print("Generating negative samples...")
    
    def generate_negatives(pos_df, num_negatives, amazon_size, google_size):
        """Generate negative samples."""
        negatives = []
        pos_set = set(zip(pos_df['ltable_id'], pos_df['rtable_id']))
        
        max_attempts = num_negatives * 10
        attempts = 0
        while len(negatives) < num_negatives and attempts < max_attempts:
            l_id = np.random.randint(0, amazon_size)
            r_id = np.random.randint(0, google_size)
            if (l_id, r_id) not in pos_set:
                negatives.append({'ltable_id': l_id, 'rtable_id': r_id})
            attempts += 1
        
        return pd.DataFrame(negatives)
    
    # Generate negatives for each split (same number as positives)
    train_neg = generate_negatives(train_pos, len(train_pos), len(amazon_df), len(google_df))
    valid_neg = generate_negatives(valid_pos, len(valid_pos), len(amazon_df), len(google_df))
    test_neg = generate_negatives(test_pos, len(test_pos), len(amazon_df), len(google_df))
    
    print(f"Train negative samples: {len(train_neg)}")
    print(f"Valid negative samples: {len(valid_neg)}")
    print(f"Test negative samples: {len(test_neg)}")
    
    # Combine positive and negative samples
    train_df = pd.concat([
        train_pos.assign(label=1),
        train_neg.assign(label=0)
    ], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
    
    valid_df = pd.concat([
        valid_pos.assign(label=1),
        valid_neg.assign(label=0)
    ], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
    
    test_df = pd.concat([
        test_pos.assign(label=1),
        test_neg.assign(label=0)
    ], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Step 5: Prepare tableA and tableB (remove original_id column for final output)
    tableA = amazon_df.drop(columns=['original_id'])
    tableB = google_df.drop(columns=['original_id'])
    
    # Step 6: Create output directory and save files
    output_dir = Path(TEMP_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving files to {output_dir}...")
    
    # Save tableA and tableB
    tableA.to_csv(output_dir / "tableA.csv", index=False)
    tableB.to_csv(output_dir / "tableB.csv", index=False)
    
    # Save train/valid/test files
    train_df.to_csv(output_dir / "train.csv", index=False)
    valid_df.to_csv(output_dir / "valid.csv", index=False)
    test_df.to_csv(output_dir / "test.csv", index=False)
    
    print("Files saved successfully!")
    print(f"  tableA.csv: {len(tableA)} rows")
    print(f"  tableB.csv: {len(tableB)} rows")
    print(f"  train.csv: {len(train_df)} rows ({len(train_pos)} positive, {len(train_neg)} negative)")
    print(f"  valid.csv: {len(valid_df)} rows ({len(valid_pos)} positive, {len(valid_neg)} negative)")
    print(f"  test.csv: {len(test_df)} rows ({len(test_pos)} positive, {len(test_neg)} negative)")
    
    return output_dir


if __name__ == "__main__":
    process_amazon_googleproducts()

