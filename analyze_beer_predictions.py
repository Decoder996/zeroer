#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析 beer 数据集的预测结果，找出高置信度的预测
"""
import pandas as pd
import numpy as np
from pathlib import Path

def analyze_predictions(dataset_name="beer", data_path="datasets"):
    dataset_path = Path(data_path) / dataset_name
    
    # 读取预测结果
    pred_file = dataset_path / "pred.csv"
    if not pred_file.exists():
        print(f"❌ 预测文件不存在: {pred_file}")
        print("请先运行 zeroer.py 生成预测结果")
        return
    
    pred_df = pd.read_csv(pred_file)
    
    # 读取真实标签
    features_file = dataset_path / "candset_features_df.csv"
    if features_file.exists():
        features_df = pd.read_csv(features_file, index_col=0)
        if 'gold' in features_df.columns:
            pred_df['gold'] = features_df['gold'].values
        else:
            print("⚠️  没有找到 gold 标签")
            pred_df['gold'] = None
    else:
        pred_df['gold'] = None
    
    print("="*70)
    print(f"Beer 数据集预测结果分析")
    print("="*70)
    print(f"\n总预测数: {len(pred_df):,}")
    print(f"预测为正样本数: {pred_df['pred'].sum():,} ({pred_df['pred'].sum()/len(pred_df)*100:.2f}%)")
    
    if pred_df['gold'] is not None and pred_df['gold'].notna().any():
        gold_pos = pred_df['gold'].sum()
        print(f"实际正样本数: {gold_pos}")
        
        # 计算混淆矩阵
        tp = ((pred_df['pred'] == 1) & (pred_df['gold'] == 1)).sum()
        fp = ((pred_df['pred'] == 1) & (pred_df['gold'] == 0)).sum()
        fn = ((pred_df['pred'] == 0) & (pred_df['gold'] == 1)).sum()
        tn = ((pred_df['pred'] == 0) & (pred_df['gold'] == 0)).sum()
        
        print(f"\n混淆矩阵:")
        print(f"  TP (真阳性): {tp}")
        print(f"  FP (假阳性): {fp:,}")
        print(f"  FN (假阴性): {fn}")
        print(f"  TN (真阴性): {tn:,}")
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"\n性能指标:")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}")
        print(f"  F1: {f1:.4f}")
    
    # 如果有概率值（如果 pred 是概率而不是 0/1）
    # 检查预测值的分布
    print(f"\n预测值分布:")
    print(pred_df['pred'].value_counts().sort_index())
    
    # 如果有 gold 标签，分析不同阈值下的性能
    if pred_df['gold'] is not None and pred_df['gold'].notna().any():
        print(f"\n" + "="*70)
        print("不同阈值下的性能（如果 pred 是概率值）")
        print("="*70)
        
        # 假设我们需要从某个地方获取概率值
        # 这里我们只能分析当前的 0/1 预测
        
        # 找出所有假阳性
        fp_df = pred_df[(pred_df['pred'] == 1) & (pred_df['gold'] == 0)]
        print(f"\n假阳性分析:")
        print(f"  假阳性总数: {len(fp_df):,}")
        print(f"  假阳性比例: {len(fp_df)/len(pred_df)*100:.2f}%")
        
        # 找出所有真阳性
        tp_df = pred_df[(pred_df['pred'] == 1) & (pred_df['gold'] == 1)]
        print(f"\n真阳性分析:")
        print(f"  真阳性总数: {len(tp_df)}")
        print(f"  真阳性比例: {len(tp_df)/len(pred_df)*100:.4f}%")
        
        # 找出所有假阴性
        fn_df = pred_df[(pred_df['pred'] == 0) & (pred_df['gold'] == 1)]
        print(f"\n假阴性分析:")
        print(f"  假阴性总数: {len(fn_df)}")
        print(f"  假阴性比例: {len(fn_df)/gold_pos*100:.2f}%")
    
    print("\n" + "="*70)
    print("建议:")
    print("="*70)
    print("1. 如果 Precision 极低，说明假阳性太多")
    print("2. 考虑使用更高的预测阈值（如果可能）")
    print("3. 检查特征质量，看是否有区分度")
    print("4. 考虑改进 blocking，减少候选对数量")
    print("="*70)

if __name__ == "__main__":
    analyze_predictions()

