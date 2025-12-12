#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试不同预测阈值对 beer 数据集性能的影响
"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import precision_score, recall_score, f1_score

def test_thresholds(dataset_name="beer", data_path="datasets"):
    dataset_path = Path(data_path) / dataset_name
    
    # 读取预测结果（概率值）
    pred_file = dataset_path / "pred.csv"
    if not pred_file.exists():
        print(f"❌ 预测文件不存在: {pred_file}")
        return
    
    pred_df = pd.read_csv(pred_file)
    
    # 读取真实标签
    features_file = dataset_path / "candset_features_df.csv"
    if features_file.exists():
        features_df = pd.read_csv(features_file, index_col=0)
        if 'gold' in features_df.columns:
            y_true = features_df['gold'].values
        else:
            print("❌ 没有找到 gold 标签")
            return
    else:
        print("❌ 没有找到特征文件")
        return
    
    # 获取概率值
    y_proba = pred_df['pred'].values
    
    print("="*70)
    print(f"Beer 数据集 - 不同阈值下的性能")
    print("="*70)
    print(f"\n总样本数: {len(y_true):,}")
    print(f"实际正样本数: {y_true.sum()}")
    print(f"预测概率范围: [{y_proba.min():.6f}, {y_proba.max():.6f}]")
    print(f"预测概率均值: {y_proba.mean():.6f}")
    print(f"预测概率中位数: {np.median(y_proba):.6f}")
    print()
    
    # 测试不同阈值
    thresholds = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
    
    results = []
    for threshold in thresholds:
        y_pred = (y_proba >= threshold).astype(int)
        
        if y_pred.sum() == 0:
            # 没有预测为正样本
            precision = 0.0
            recall = 0.0
            f1 = 0.0
            pred_pos = 0
        else:
            precision = precision_score(y_true, y_pred, zero_division=0)
            recall = recall_score(y_true, y_pred, zero_division=0)
            f1 = f1_score(y_true, y_pred, zero_division=0)
            pred_pos = y_pred.sum()
        
        results.append({
            'threshold': threshold,
            'pred_pos': pred_pos,
            'precision': precision,
            'recall': recall,
            'f1': f1
        })
    
    # 打印结果表格
    print(f"{'阈值':<10} {'预测正样本':<15} {'Precision':<12} {'Recall':<12} {'F1':<12}")
    print("-" * 70)
    for r in results:
        print(f"{r['threshold']:<10.2f} {r['pred_pos']:<15,} {r['precision']:<12.4f} {r['recall']:<12.4f} {r['f1']:<12.4f}")
    
    # 找出最佳阈值（F1最高）
    best_f1_idx = np.argmax([r['f1'] for r in results])
    best = results[best_f1_idx]
    
    print("\n" + "="*70)
    print("最佳阈值（基于 F1）:")
    print("="*70)
    print(f"  阈值: {best['threshold']:.2f}")
    print(f"  预测正样本数: {best['pred_pos']:,}")
    print(f"  Precision: {best['precision']:.4f}")
    print(f"  Recall: {best['recall']:.4f}")
    print(f"  F1: {best['f1']:.4f}")
    
    # 找出 Precision 最高的阈值（如果 Precision > 0.1）
    high_precision = [r for r in results if r['precision'] > 0.1]
    if high_precision:
        best_prec = max(high_precision, key=lambda x: x['precision'])
        print("\n" + "="*70)
        print("高 Precision 阈值（Precision > 0.1）:")
        print("="*70)
        print(f"  阈值: {best_prec['threshold']:.2f}")
        print(f"  预测正样本数: {best_prec['pred_pos']:,}")
        print(f"  Precision: {best_prec['precision']:.4f}")
        print(f"  Recall: {best_prec['recall']:.4f}")
        print(f"  F1: {best_prec['f1']:.4f}")
    
    print("\n" + "="*70)
    print("建议:")
    print("="*70)
    print("1. 如果目标是最大化 F1，使用最佳阈值")
    print("2. 如果目标是减少假阳性（提高 Precision），使用更高阈值")
    print("3. 如果目标是找到更多正样本（提高 Recall），使用更低阈值")
    print("="*70)

if __name__ == "__main__":
    test_thresholds()

