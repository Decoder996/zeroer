#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score

# Load predictions and ground truth
df = pd.read_csv('datasets/walmart_amazon_dirty/pred.csv')
matches = pd.read_csv('datasets/walmart_amazon_dirty/matches.csv')

# Create match set for fast lookup
match_set = set(zip(matches['ltable_id'], matches['rtable_id']))

# Add true labels
df['true_label'] = df.apply(lambda row: 1 if (row['ltable_id'], row['rtable_id']) in match_set else 0, axis=1)

# Calculate predictions with threshold 0.5
df['pred_label'] = (df['pred'] >= 0.5).astype(int)

# Calculate metrics
if df['true_label'].sum() > 0:
    p = precision_score(df['true_label'], df['pred_label'])
    r = recall_score(df['true_label'], df['pred_label'])
    f1 = f1_score(df['true_label'], df['pred_label'])
    
    print("="*60)
    print("ZeroER Results for Walmart-Amazon Dirty")
    print("="*60)
    print(f'F1 Score:     {f1:.4f}')
    print(f'Precision:    {p:.4f}')
    print(f'Recall:       {r:.4f}')
    print("="*60)
    print(f'Total candidate pairs: {len(df)}')
    print(f'Ground truth matches:  {df["true_label"].sum()}')
    print(f'Predicted matches:     {df["pred_label"].sum()}')
    print(f'True positives:        {((df["true_label"] == 1) & (df["pred_label"] == 1)).sum()}')
    print(f'False positives:       {((df["true_label"] == 0) & (df["pred_label"] == 1)).sum()}')
    print(f'False negatives:       {((df["true_label"] == 1) & (df["pred_label"] == 0)).sum()}')
    print("="*60)
else:
    print('No ground truth labels found in candidate set')

