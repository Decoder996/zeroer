import os
# Set BLAS environment variables before any imports
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['GOTO_NUM_THREADS'] = '1'

import pandas as pd
import numpy as np

# Test reading the file
print("Testing CSV read...")
df = pd.read_csv('datasets/amazon_googleproducts/candset_features_df.csv', index_col=0, nrows=1000)
print(f"Successfully read {len(df)} rows, {len(df.columns)} columns")
print("BLAS configuration test passed!")
