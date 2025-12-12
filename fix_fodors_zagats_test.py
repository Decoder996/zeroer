#!/usr/bin/env python3
"""
修复 fodors_zagats_test 数据集的字符串格式问题

这个脚本会：
1. 清理字符串格式（反引号 -> 单引号）
2. 移除多余的转义和空格
3. 重新生成 matches 文件（如果需要）
"""

import pandas as pd
import os
from pathlib import Path

def clean_string(s):
    """清理字符串格式，使其与原始 fodors_zagats 一致"""
    if pd.isna(s):
        return s
    
    s = str(s)
    # 移除反引号
    s = s.replace('`', '')
    # 清理转义格式：\ ' -> '（保留单引号，但要小心处理）
    # 先处理空格+转义+单引号的组合，替换成单引号+空格
    s = s.replace(" \\ '", " '")
    s = s.replace("\\ '", "'")
    s = s.replace(" \\'", "'")
    
    # 清理前后空格和单引号（可能是外层引号）
    s = s.strip()
    # 如果前后有单引号，先去掉（可能是外层引号）
    if s.startswith("'") and s.endswith("'"):
        # 检查是否是外层引号（前后都有，且中间有内容）
        if len(s) > 2:
            inner = s[1:-1].strip()
        else:
            inner = ""
    else:
        inner = s
    
    # 清理中间多余空格（但保留必要的空格）
    inner = ' '.join(inner.split())
    
    # 转义内部单引号（CSV 格式要求）
    inner = inner.replace("'", "\\'")
    # 加上外层单引号（与原始格式一致）
    s = f"'{inner}'"
    
    return s

def fix_dataset(dataset_path):
    """修复数据集"""
    dataset_path = Path(dataset_path)
    
    print(f"修复数据集: {dataset_path}")
    print("="*60)
    
    # 修复 fodors.csv
    fodors_file = dataset_path / "fodors.csv"
    if fodors_file.exists():
        print(f"\n修复 {fodors_file}...")
        df = pd.read_csv(fodors_file)
        
        # 备份原文件
        backup_file = dataset_path / "fodors.csv.backup"
        if not backup_file.exists():
            df.to_csv(backup_file, index=False)
            print(f"  已备份到 {backup_file}")
        
        # 清理字符串列
        string_cols = ['name', 'addr', 'city', 'phone', 'type']
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].apply(clean_string)
                print(f"  已清理 {col} 列")
        
        # 保存
        df.to_csv(fodors_file, index=False)
        print(f"  ✓ 已修复 {fodors_file}")
    else:
        print(f"  ⚠️  文件不存在: {fodors_file}")
    
    # 修复 zagats.csv
    zagats_file = dataset_path / "zagats.csv"
    if zagats_file.exists():
        print(f"\n修复 {zagats_file}...")
        df = pd.read_csv(zagats_file)
        
        # 备份原文件
        backup_file = dataset_path / "zagats.csv.backup"
        if not backup_file.exists():
            df.to_csv(backup_file, index=False)
            print(f"  已备份到 {backup_file}")
        
        # 清理字符串列
        string_cols = ['name', 'addr', 'city', 'phone', 'type']
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].apply(clean_string)
                print(f"  已清理 {col} 列")
        
        # 保存
        df.to_csv(zagats_file, index=False)
        print(f"  ✓ 已修复 {zagats_file}")
    else:
        print(f"  ⚠️  文件不存在: {zagats_file}")
    
    # 检查 matches 文件
    matches_file = dataset_path / "matches_fodors_zagats.csv"
    if matches_file.exists():
        print(f"\n检查 {matches_file}...")
        matches = pd.read_csv(matches_file)
        print(f"  Matches 数量: {len(matches)}")
        print(f"  列名: {list(matches.columns)}")
        
        # 检查是否有重复
        if len(matches) != len(matches.drop_duplicates()):
            print(f"  ⚠️  发现重复，去重后: {len(matches.drop_duplicates())}")
            matches = matches.drop_duplicates()
            matches.to_csv(matches_file, index=False)
            print(f"  ✓ 已去重并保存")
    
    print("\n" + "="*60)
    print("修复完成！")
    print("\n下一步：")
    print("1. 删除旧的特征文件: rm datasets/fodors_zagats_test/candset_features_df.csv")
    print("2. 重新运行: python zeroer.py fodors_zagats_test")
    print("="*60)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    else:
        dataset_path = "datasets/fodors_zagats_test"
    
    fix_dataset(dataset_path)

