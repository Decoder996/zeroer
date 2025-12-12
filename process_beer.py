#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Process Beer dataset from datasets_raw/Structured/Beer to ZeroER format.

This script uses convert_raw_to_dataset.py to convert the Beer dataset.
"""

import sys
from pathlib import Path
from convert_raw_to_dataset import convert_dataset

# Configuration for Beer dataset
SOURCE_DIR = "datasets_raw/Structured/Beer"
TARGET_DATASET_NAME = "beer"
LEFT_TABLE_NAME = "tableA.csv"
RIGHT_TABLE_NAME = "tableB.csv"
MATCHES_FILE_NAME = "matches.csv"

if __name__ == "__main__":
    print("="*60)
    print("Processing Beer dataset for ZeroER")
    print("="*60)
    
    convert_dataset(
        source_dir=SOURCE_DIR,
        target_dataset_name=TARGET_DATASET_NAME,
        left_table_name=LEFT_TABLE_NAME,
        right_table_name=RIGHT_TABLE_NAME,
        matches_file_name=MATCHES_FILE_NAME,
        use_train=True,
        use_valid=True,
        use_test=True
    )
    
    print("\n✅ Beer dataset processing completed!")
    print(f"\nNext steps:")
    print(f"1. Add blocking function to blocking_functions.py")
    print(f"2. Run: python zeroer.py beer")

