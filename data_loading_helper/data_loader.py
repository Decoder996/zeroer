import pandas as pd
from pandas import merge
import py_entitymatching as em
import sys

def load_data(left_file_name, right_file_name, label_file_name, blocking_fn, include_self_join=False):
    print(f"[LOAD_DATA] Starting data loading...", flush=True)
    print(f"[LOAD_DATA] Loading left table: {left_file_name}", flush=True)
    A = em.read_csv_metadata(left_file_name , key="id", encoding='iso-8859-1')
    print(f"[LOAD_DATA] Left table loaded: {len(A)} rows, columns: {list(A.columns)}", flush=True)
    
    print(f"[LOAD_DATA] Loading right table: {right_file_name}", flush=True)
    B = em.read_csv_metadata(right_file_name , key="id", encoding='iso-8859-1')
    print(f"[LOAD_DATA] Right table loaded: {len(B)} rows, columns: {list(B.columns)}", flush=True)
    
    try:
        G = pd.read_csv(label_file_name)
        print(f"[LOAD_DATA] Ground truth loaded: {len(G)} matches", flush=True)
    except:
        G=None
        print(f"[LOAD_DATA] No ground truth file found", flush=True)
    
    print(f"[LOAD_DATA] Starting blocking (LxR)...", flush=True)
    sys.stdout.flush()
    C = blocking_fn(A, B)
    print(f"[LOAD_DATA] Blocking (LxR) completed: {len(C)} candidate pairs", flush=True)
    
    if include_self_join:
        print(f"[LOAD_DATA] Starting self-join blocking (LxL)...", flush=True)
        sys.stdout.flush()
        C_A = blocking_fn(A, A)
        print(f"[LOAD_DATA] Blocking (LxL) completed: {len(C_A)} candidate pairs", flush=True)
        
        print(f"[LOAD_DATA] Starting self-join blocking (RxR)...", flush=True)
        sys.stdout.flush()
        C_B = blocking_fn(B, B)
        print(f"[LOAD_DATA] Blocking (RxR) completed: {len(C_B)} candidate pairs", flush=True)
        return A, B, G, C, C_A,C_B
    else:
        return A, B, G, C
