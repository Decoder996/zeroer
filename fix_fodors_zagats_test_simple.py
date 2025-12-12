#!/usr/bin/env python3
"""
简化版修复脚本：直接修复字符串格式问题
"""

import pandas as pd
import re
from pathlib import Path

def clean_string(s):
    """清理字符串格式，使其与原始 fodors_zagats 一致"""
    if pd.isna(s):
        return s
    
    s = str(s)
    # 移除反引号
    s = s.replace('`', '')
    # 清理转义格式：空格+反斜杠+空格+单引号 -> 单引号
    s = s.replace(" \\ '", "'")
    s = s.replace("\\ '", "'")
    # 清理前后空格和单引号（可能是外层引号）
    s = s.strip()
    # 如果末尾有单独的单引号（可能是外层引号），去掉
    if s.endswith(" '") or s.endswith("'"):
        # 检查是否是外层引号（末尾单独的单引号）
        s = s.rstrip(" '")
        s = s.rstrip("'")
    # 如果开头有单独的单引号，去掉
    if s.startswith("' ") or s.startswith("'"):
        s = s.lstrip("' ")
        s = s.lstrip("'")
    # 再次清理空格
    s = s.strip()
    # 清理中间多余空格（包括点号前的空格）
    s = ' '.join(s.split())
    # 清理点号前的空格
    s = s.replace(' .', '.')
    s = s.replace(' ,', ',')
    # 转义内部单引号
    s = s.replace("'", "\\'")
    # 加上外层单引号
    return f"'{s}'"

def fix_dataset(dataset_path="datasets/fodors_zagats_test"):
    """修复数据集"""
    dataset_path = Path(dataset_path)
    
    print(f"修复数据集: {dataset_path}")
    print("="*60)
    
    # 修复 fodors.csv
    for file_name in ["fodors.csv", "zagats.csv"]:
        file_path = dataset_path / file_name
        if not file_path.exists():
            print(f"⚠️  文件不存在: {file_path}")
            continue
        
        print(f"\n修复 {file_name}...")
        df = pd.read_csv(file_path)
        
        # 备份
        backup_file = dataset_path / f"{file_name}.backup"
        if not backup_file.exists():
            df.to_csv(backup_file, index=False)
            print(f"  ✓ 已备份到 {backup_file}")
        
        # 清理字符串列
        string_cols = ['name', 'addr', 'city', 'phone', 'type']
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].apply(clean_string)
        
        # 保存
        df.to_csv(file_path, index=False)
        print(f"  ✓ 已修复 {file_name}")
    
    print("\n" + "="*60)
    print("修复完成！")
    print("\n下一步：")
    print("  rm datasets/fodors_zagats_test/candset_features_df.csv")
    print("  python zeroer.py fodors_zagats_test")
    print("="*60)

if __name__ == '__main__':
    import sys
    dataset_path = sys.argv[1] if len(sys.argv) > 1 else "datasets/fodors_zagats_test"
    fix_dataset(dataset_path)

