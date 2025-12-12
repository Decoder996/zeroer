#!/usr/bin/env python3
"""
通用数据集转换脚本
将 datasets_raw 中的 deepmatcher 格式数据集转换为 zeroER 格式

使用方法:
    python convert_any_dataset.py <source_dir> <target_name> [--left_name LEFT] [--right_name RIGHT] [--matches_name MATCHES]

示例:
    python convert_any_dataset.py datasets_raw/Structured/DBLP-ACM dblp_acm
    python convert_any_dataset.py datasets_raw/Structured/iTunes-Amazon itunes_amazon --left_name tableA.csv --right_name tableB.csv
"""

import sys
import argparse
from pathlib import Path
from convert_raw_to_dataset import convert_dataset

def main():
    parser = argparse.ArgumentParser(description='Convert deepmatcher dataset to zeroER format')
    parser.add_argument('source_dir', type=str, help='Source directory in datasets_raw (e.g., datasets_raw/Structured/DBLP-ACM)')
    parser.add_argument('target_name', type=str, help='Target dataset name (e.g., dblp_acm)')
    parser.add_argument('--left_name', type=str, default='tableA.csv', help='Left table file name (default: tableA.csv)')
    parser.add_argument('--right_name', type=str, default='tableB.csv', help='Right table file name (default: tableB.csv)')
    parser.add_argument('--matches_name', type=str, default='matches.csv', help='Matches file name (default: matches.csv)')
    parser.add_argument('--no-train', action='store_true', help='Exclude train.csv matches')
    parser.add_argument('--no-valid', action='store_true', help='Exclude valid.csv matches')
    parser.add_argument('--no-test', action='store_true', help='Exclude test.csv matches')
    
    args = parser.parse_args()
    
    # Check if source directory exists
    source_path = Path(args.source_dir)
    if not source_path.exists():
        print(f"❌ Error: Source directory not found: {source_path}")
        print(f"\nAvailable datasets in datasets_raw/Structured/:")
        structured_path = Path("datasets_raw/Structured")
        if structured_path.exists():
            for d in sorted(structured_path.iterdir()):
                if d.is_dir():
                    print(f"  - {d.name}")
        sys.exit(1)
    
    print("="*60)
    print(f"Converting dataset: {args.source_dir} -> {args.target_name}")
    print("="*60)
    
    try:
        convert_dataset(
            source_dir=args.source_dir,
            target_dataset_name=args.target_name,
            left_table_name=args.left_name,
            right_table_name=args.right_name,
            matches_file_name=args.matches_name,
            use_train=not args.no_train,
            use_valid=not args.no_valid,
            use_test=not args.no_test
        )
        
        print("\n✅ Conversion completed successfully!")
        print("\n" + "="*60)
        print("Next steps:")
        print("="*60)
        print(f"1. Add blocking function to blocking_functions.py")
        print(f"   (Check existing blocking functions for reference)")
        print(f"2. Add mapping in blocking_functions.py:")
        print(f"   blocking_functions_mapping[\"{args.target_name}\"] = block_<your_function>")
        print(f"3. Run zeroER:")
        print(f"   python zeroer.py {args.target_name}")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

