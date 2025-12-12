#!/usr/bin/env python3
"""
Diagnostic script for zeroER issues
This script helps identify why zeroER might be running slowly or producing poor results
"""

import pandas as pd
import numpy as np
import os
from os.path import join
import sys

def diagnose_dataset(dataset_name, data_path="datasets"):
    """Diagnose a dataset to identify potential issues"""
    print(f"\n{'='*60}")
    print(f"Diagnosing dataset: {dataset_name}")
    print(f"{'='*60}\n")
    
    dataset_path = join(data_path, dataset_name)
    
    # Check if feature file exists
    feature_file = join(dataset_path, "candset_features_df.csv")
    if not os.path.exists(feature_file):
        print(f"❌ Feature file not found: {feature_file}")
        print("   You need to run zeroer.py first to generate features.")
        return
    
    print(f"✓ Feature file found: {feature_file}")
    
    # Load features
    try:
        candset_features_df = pd.read_csv(feature_file, index_col=0)
        candset_features_df.reset_index(drop=True, inplace=True)
        print(f"✓ Successfully loaded features")
    except Exception as e:
        print(f"❌ Error loading features: {e}")
        return
    
    # Basic statistics
    print(f"\n📊 Basic Statistics:")
    print(f"   Total candidate pairs: {len(candset_features_df):,}")
    
    # Check for gold labels
    if 'gold' in candset_features_df.columns:
        gold_counts = candset_features_df['gold'].value_counts()
        print(f"   Gold labels distribution:")
        for label, count in gold_counts.items():
            print(f"     Label {label}: {count:,} ({count/len(candset_features_df)*100:.2f}%)")
    else:
        print("   ⚠️  No gold labels found (this is normal for test datasets)")
    
    # Get similarity features
    try:
        from data_loading_helper.feature_extraction import gather_similarity_features
        similarity_features_df = gather_similarity_features(candset_features_df)
        print(f"\n📈 Similarity Features:")
        print(f"   Number of similarity features: {len(similarity_features_df.columns)}")
        print(f"   Feature names (first 10): {list(similarity_features_df.columns[:10])}")
    except Exception as e:
        print(f"❌ Error extracting similarity features: {e}")
        return
    
    # Check feature statistics
    print(f"\n🔍 Feature Statistics:")
    feature_stats = similarity_features_df.describe()
    print(f"   Feature value ranges:")
    print(f"     Min: {feature_stats.loc['min'].min():.4f}")
    print(f"     Max: {feature_stats.loc['max'].max():.4f}")
    print(f"     Mean: {feature_stats.loc['mean'].mean():.4f}")
    print(f"     Std: {feature_stats.loc['std'].mean():.4f}")
    
    # Check for problematic features
    print(f"\n⚠️  Potential Issues:")
    
    # Check for NaN or infinite values
    nan_counts = similarity_features_df.isna().sum()
    inf_counts = np.isinf(similarity_features_df).sum()
    if nan_counts.sum() > 0:
        print(f"   ❌ Found {nan_counts.sum()} NaN values in features")
        print(f"      Columns with NaN: {nan_counts[nan_counts > 0].to_dict()}")
    else:
        print(f"   ✓ No NaN values")
    
    if inf_counts.sum() > 0:
        print(f"   ❌ Found {inf_counts.sum()} infinite values in features")
    else:
        print(f"   ✓ No infinite values")
    
    # Check for constant features (should have been removed, but check anyway)
    constant_features = similarity_features_df.nunique() == 1
    if constant_features.sum() > 0:
        print(f"   ⚠️  Found {constant_features.sum()} constant features (should be removed)")
        print(f"      Constant features: {list(similarity_features_df.columns[constant_features])}")
    else:
        print(f"   ✓ No constant features")
    
    # Check feature scale
    feature_ranges = similarity_features_df.max() - similarity_features_df.min()
    very_small_range = feature_ranges < 0.001
    if very_small_range.sum() > 0:
        print(f"   ⚠️  Found {very_small_range.sum()} features with very small range (<0.001)")
    
    # Check initialization
    print(f"\n🎯 Initialization Check:")
    try:
        from model import get_y_init_given_threshold
        from sklearn.preprocessing import MinMaxScaler
        
        # Check initialization threshold
        x = similarity_features_df.values
        min_max_scaler = MinMaxScaler()
        x_scaled = min_max_scaler.fit_transform(x)
        scaled_sum = np.sum(x_scaled, axis=1)
        scaled_sum_normalized = MinMaxScaler().fit_transform(scaled_sum.reshape(-1,1)).flatten()
        
        threshold = 0.8
        y_init = scaled_sum_normalized > threshold
        init_positive = y_init.sum()
        init_negative = (~y_init).sum()
        
        print(f"   Initialization threshold: {threshold}")
        print(f"   Initial positive predictions: {init_positive:,} ({init_positive/len(y_init)*100:.2f}%)")
        print(f"   Initial negative predictions: {init_negative:,} ({init_negative/len(y_init)*100:.2f}%)")
        
        if init_positive < 10:
            print(f"   ⚠️  Very few initial positive predictions! This might cause poor performance.")
        elif init_positive > len(y_init) * 0.5:
            print(f"   ⚠️  Too many initial positive predictions! This might cause poor performance.")
        else:
            print(f"   ✓ Initialization looks reasonable")
            
    except Exception as e:
        print(f"   ❌ Error checking initialization: {e}")
        import traceback
        traceback.print_exc()
    
    # Check blocking quality
    print(f"\n🔒 Blocking Quality:")
    if 'gold' in candset_features_df.columns:
        total_pairs = len(candset_features_df)
        positive_pairs = candset_features_df['gold'].sum()
        if positive_pairs > 0:
            positive_ratio = positive_pairs / total_pairs
            print(f"   Positive pairs ratio: {positive_ratio:.4f} ({positive_ratio*100:.2f}%)")
            if positive_ratio < 0.001:
                print(f"   ⚠️  Very low positive ratio! Blocking might be too loose.")
            elif positive_ratio > 0.1:
                print(f"   ⚠️  High positive ratio! Blocking might be too strict.")
            else:
                print(f"   ✓ Blocking ratio looks reasonable")
    
    # Performance estimation
    print(f"\n⚡ Performance Estimation:")
    print(f"   Feature matrix size: {similarity_features_df.shape[0]:,} x {similarity_features_df.shape[1]}")
    print(f"   Estimated memory (MB): {similarity_features_df.memory_usage(deep=True).sum() / 1024**2:.2f}")
    
    # EM algorithm complexity is roughly O(n * m * iterations)
    # where n is number of samples, m is number of features
    n_samples = similarity_features_df.shape[0]
    n_features = similarity_features_df.shape[1]
    n_iterations = 40  # default max_iter
    
    # Rough estimate: each iteration involves matrix operations
    # For large datasets, this can be slow
    if n_samples > 100000:
        print(f"   ⚠️  Large candidate set ({n_samples:,} pairs) - EM will be slow")
        print(f"      Consider using better blocking to reduce candidate pairs")
    elif n_samples > 50000:
        print(f"   ⚠️  Medium candidate set ({n_samples:,} pairs) - EM might be slow")
    else:
        print(f"   ✓ Candidate set size looks manageable")
    
    if n_features > 200:
        print(f"   ⚠️  Many features ({n_features}) - might slow down EM")
    else:
        print(f"   ✓ Feature count looks reasonable")
    
    print(f"\n{'='*60}\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python diagnose_zeroer.py <dataset_name>")
        print("Example: python diagnose_zeroer.py fodors_zagats")
        sys.exit(1)
    
    dataset_name = sys.argv[1]
    diagnose_dataset(dataset_name)

