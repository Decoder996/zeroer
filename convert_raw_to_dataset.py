#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convert raw datasets from datasets_raw to datasets format for ZeroER.

This script converts datasets from the raw format (with tableA.csv, tableB.csv, 
train.csv, valid.csv, test.csv) to the format required by ZeroER (with left table,
right table, matches file, and metadata.txt).
"""

import pandas as pd
import os
import shutil
from pathlib import Path


# ============================================================================
# Configuration - Modify these parameters for different datasets
# ============================================================================

# Source directory in datasets_raw
SOURCE_DIR = "datasets_raw/Structured/Amazon-GoogleProducts"

# Target directory name in datasets (will be created under datasets/)
TARGET_DATASET_NAME = "amazon_googleproducts"

# File names for the converted dataset
LEFT_TABLE_NAME = "tableA.csv"      # Left table file name in target directory
RIGHT_TABLE_NAME = "tableB.csv"     # Right table file name in target directory
MATCHES_FILE_NAME = "matches.csv"   # Matches file name in target directory

# Whether to use all splits (train+valid+test) or only specific ones
USE_TRAIN = True
USE_VALID = True
USE_TEST = True

# ============================================================================


def convert_dataset(source_dir, target_dataset_name, left_table_name, 
                   right_table_name, matches_file_name, 
                   use_train=True, use_valid=True, use_test=True):
    """
    Convert raw dataset to ZeroER format.
    
    Args:
        source_dir: Path to source directory in datasets_raw (e.g., "datasets_raw/Structured/Amazon-Google")
        target_dataset_name: Name of target dataset directory (e.g., "amazon_google")
        left_table_name: Name for left table file in target directory
        right_table_name: Name for right table file in target directory
        matches_file_name: Name for matches file in target directory
        use_train: Whether to include train.csv matches
        use_valid: Whether to include valid.csv matches
        use_test: Whether to include test.csv matches
    """
    # Convert to Path objects for easier path handling
    source_path = Path(source_dir)
    target_path = Path("datasets") / target_dataset_name
    
    # Check if source directory exists
    if not source_path.exists():
        raise FileNotFoundError(f"Source directory not found: {source_path}")
    
    # Create target directory
    target_path.mkdir(parents=True, exist_ok=True)
    print(f"Created target directory: {target_path}")
    
    # Step 1: Copy tableA.csv and tableB.csv
    tableA_source = source_path / "tableA.csv"
    tableB_source = source_path / "tableB.csv"
    
    if not tableA_source.exists():
        raise FileNotFoundError(f"tableA.csv not found in {source_path}")
    if not tableB_source.exists():
        raise FileNotFoundError(f"tableB.csv not found in {source_path}")
    
    tableA_target = target_path / left_table_name
    tableB_target = target_path / right_table_name
    
    print(f"Copying {tableA_source} -> {tableA_target}")
    shutil.copy2(tableA_source, tableA_target)
    
    print(f"Copying {tableB_source} -> {tableB_target}")
    shutil.copy2(tableB_source, tableB_target)
    
    # Step 2: Extract matches from train.csv, valid.csv, test.csv
    matches_list = []
    
    if use_train:
        train_file = source_path / "train.csv"
        if train_file.exists():
            print(f"Reading matches from {train_file}")
            train_df = pd.read_csv(train_file)
            # Filter for positive matches (label == 1)
            train_matches = train_df[train_df['label'] == 1][['ltable_id', 'rtable_id']]
            matches_list.append(train_matches)
            print(f"  Found {len(train_matches)} matches in train.csv")
        else:
            print(f"Warning: {train_file} not found, skipping")
    
    if use_valid:
        valid_file = source_path / "valid.csv"
        if valid_file.exists():
            print(f"Reading matches from {valid_file}")
            valid_df = pd.read_csv(valid_file)
            # Filter for positive matches (label == 1)
            valid_matches = valid_df[valid_df['label'] == 1][['ltable_id', 'rtable_id']]
            matches_list.append(valid_matches)
            print(f"  Found {len(valid_matches)} matches in valid.csv")
        else:
            print(f"Warning: {valid_file} not found, skipping")
    
    if use_test:
        test_file = source_path / "test.csv"
        if test_file.exists():
            print(f"Reading matches from {test_file}")
            test_df = pd.read_csv(test_file)
            # Filter for positive matches (label == 1)
            test_matches = test_df[test_df['label'] == 1][['ltable_id', 'rtable_id']]
            matches_list.append(test_matches)
            print(f"  Found {len(test_matches)} matches in test.csv")
        else:
            print(f"Warning: {test_file} not found, skipping")
    
    if not matches_list:
        raise ValueError("No matches found in any of the split files!")
    
    # Combine all matches and remove duplicates
    all_matches = pd.concat(matches_list, ignore_index=True)
    all_matches = all_matches.drop_duplicates()
    print(f"Total unique matches: {len(all_matches)}")
    
    # Save matches file
    matches_target = target_path / matches_file_name
    all_matches.to_csv(matches_target, index=False)
    print(f"Saved matches to {matches_target}")
    
    # Step 3: Create metadata.txt
    metadata_file = target_path / "metadata.txt"
    with open(metadata_file, 'w') as f:
        f.write(f"{left_table_name}\n")
        f.write(f"{right_table_name}\n")
        f.write(f"{matches_file_name}\n")
    print(f"Created metadata.txt: {metadata_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("Conversion completed successfully!")
    print("="*60)
    print(f"Source: {source_path}")
    print(f"Target: {target_path}")
    print(f"Left table: {left_table_name}")
    print(f"Right table: {right_table_name}")
    print(f"Matches: {matches_file_name} ({len(all_matches)} matches)")
    print("="*60)


if __name__ == "__main__":
    convert_dataset(
        source_dir=SOURCE_DIR,
        target_dataset_name=TARGET_DATASET_NAME,
        left_table_name=LEFT_TABLE_NAME,
        right_table_name=RIGHT_TABLE_NAME,
        matches_file_name=MATCHES_FILE_NAME,
        use_train=USE_TRAIN,
        use_valid=USE_VALID,
        use_test=USE_TEST
    )

