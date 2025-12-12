# Fix OpenBLAS memory allocation issue for large matrices
# MUST set environment variables BEFORE importing any libraries that use BLAS
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['GOTO_NUM_THREADS'] = '1'
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'

from data_loading_helper.data_loader import load_data
from data_loading_helper.feature_extraction import *
from utils import run_zeroer
from blocking_functions import *
from os.path import join
import argparse
import sys
parser = argparse.ArgumentParser()
parser.add_argument("dataset",type=str)
parser.add_argument("--run_transitivity",type=bool,default=False,nargs="?",const=True, help="whether to enforce transitivity constraint")
parser.add_argument("--LR_dup_free",type=bool,default=False,nargs="?",const=True, help="are the left table and right table duplicate-free?")
parser.add_argument("--LR_identical",type=bool,default=False,nargs="?",const=True, help="are the left table and right table identical?")
parser.add_argument("--n_jobs",type=int,default=4, help="number of parallel jobs for feature extraction (default: 4, use -1 for all cores)")
parser.add_argument("--init_threshold",type=float,default=0.8, help="initialization threshold for positive samples (default: 0.8, paper default: 0.5)")
parser.add_argument("--c_bay",type=float,default=0.015, help="regularization parameter kappa' (default: 0.015, paper default: 0.01, range: [0, 0.1])")

data_path = "datasets"

if __name__ == '__main__':
    args = parser.parse_args()
    LR_dup_free = args.LR_dup_free
    run_trans = args.run_transitivity
    LR_identical = args.LR_identical
    dataset_name = args.dataset
    n_jobs = args.n_jobs
    init_threshold = args.init_threshold
    c_bay = args.c_bay
    dataset_path = join(data_path,dataset_name)
    blocking_func = blocking_functions_mapping[dataset_name]
    
    # Set environment variable for feature extraction
    import os
    os.environ['ZEROER_N_JOBS'] = str(n_jobs)
    print(f"Using {n_jobs} parallel jobs for feature extraction (set --n_jobs to change)")
    try:
        candset_features_df = pd.read_csv(join(dataset_path,"candset_features_df.csv"), index_col=0)
        candset_features_df.reset_index(drop=True,inplace=True)
        if run_trans==True:
            id_df = candset_features_df[["ltable_id","rtable_id"]]
            id_df.reset_index(drop=True,inplace=True)
            if LR_dup_free==False and LR_identical==False:
                candset_features_df_l = pd.read_csv(join(dataset_path,"candset_features_df_l.csv"), index_col=0)
                candset_features_df_l.reset_index(drop=True,inplace=True)
                candset_features_df_r = pd.read_csv(join(dataset_path,"candset_features_df_r.csv"), index_col=0)
                candset_features_df_r.reset_index(drop=True,inplace=True)
                id_df_l = candset_features_df_l[["ltable_id","rtable_id"]]
                id_df_l.reset_index(drop=True,inplace=True)
                id_df_r = candset_features_df_r[["ltable_id","rtable_id"]]
                id_df_r.reset_index(drop=True,inplace=True)
        print(
            "Features already generated, reading from file: " + dataset_path + "/candset_features_df.csv")

    except FileNotFoundError:
        print("Generating features and storing in: " + dataset_path + "/candset_features_df.csv", flush=True)
        print(f"[ZEROER] Dataset: {dataset_name}", flush=True)
        print(f"[ZEROER] Transitivity: {run_trans}, LR_dup_free: {LR_dup_free}, LR_identical: {LR_identical}", flush=True)

        f = open(join(dataset_path, 'metadata.txt'), "r")
        LEFT_FILE = join(dataset_path, f.readline().strip())
        if LR_identical:
            RIGHT_FILE = LEFT_FILE
        else:
            RIGHT_FILE = join(dataset_path, f.readline().strip())
        DUPLICATE_TUPLES = join(dataset_path, f.readline().strip())
        f.close()
        print(f"[ZEROER] Files: LEFT={LEFT_FILE}, RIGHT={RIGHT_FILE}, MATCHES={DUPLICATE_TUPLES}", flush=True)
        if run_trans==True and LR_dup_free==False and LR_identical==False:
            ltable_df, rtable_df, duplicates_df, candset_df,candset_df_l,candset_df_r = load_data(LEFT_FILE, RIGHT_FILE, DUPLICATE_TUPLES,
                                                                                              blocking_func,
                                                                                              include_self_join=True)
        else:
            ltable_df, rtable_df, duplicates_df, candset_df = load_data(LEFT_FILE, RIGHT_FILE, DUPLICATE_TUPLES,
                                                                                              blocking_func,
                                                                                              include_self_join=False)
            if LR_identical:
                print("removing self matches")
                candset_df = candset_df.loc[candset_df.ltable_id!=candset_df.rtable_id,:]
                candset_df.reset_index(inplace=True,drop=True)
                candset_df['_id'] = candset_df.index
        if duplicates_df is None:
            duplicates_df = pd.DataFrame(columns=["ltable_id", "rtable_id"])
        print(f"[ZEROER] Starting feature extraction for {len(candset_df):,} candidate pairs...", flush=True)
        sys.stdout.flush()
        candset_features_df = gather_features_and_labels(ltable_df, rtable_df, duplicates_df, candset_df)
        print(f"[ZEROER] Feature extraction completed. Saving to file...", flush=True)
        sys.stdout.flush()
        candset_features_df.to_csv(join(dataset_path,"candset_features_df.csv"))
        print(f"[ZEROER] Features saved: {len(candset_features_df):,} rows, {len(candset_features_df.columns)} columns", flush=True)
        id_df = candset_df[["ltable_id", "rtable_id"]]

        if run_trans == True and LR_dup_free == False and LR_identical==False:
            duplicates_df_r = pd.DataFrame()
            duplicates_df_r['l_id'] = rtable_df["id"]
            duplicates_df_r['r_id'] = rtable_df["id"]
            candset_features_df_r = gather_features_and_labels(rtable_df, rtable_df, duplicates_df_r, candset_df_r)
            candset_features_df_r.to_csv(join(dataset_path,"candset_features_df_r.csv"))


            duplicates_df_l = pd.DataFrame()
            duplicates_df_l['l_id'] = ltable_df["id"]
            duplicates_df_l['r_id'] = ltable_df["id"]
            candset_features_df_l = gather_features_and_labels(ltable_df, ltable_df, duplicates_df_l, candset_df_l)
            candset_features_df_l.to_csv(join(dataset_path,"candset_features_df_l.csv"))

            id_df_l = candset_df_l[["ltable_id","rtable_id"]]
            id_df_r = candset_df_r[["ltable_id","rtable_id"]]
            id_df_l.to_csv(join(dataset_path,"id_tuple_df_l.csv"))
            id_df_r.to_csv(join(dataset_path,"id_tuple_df_r.csv"))

    similarity_features_df = gather_similarity_features(candset_features_df)
    similarity_features_lr = (None,None)
    id_dfs = (None, None, None)
    if run_trans == True:
        id_dfs = (id_df, None, None)
        if LR_dup_free == False and LR_identical==False:
            similarity_features_df_l = gather_similarity_features(candset_features_df_l)
            similarity_features_df_r = gather_similarity_features(candset_features_df_r)
            features = set(similarity_features_df.columns)
            features = features.intersection(set(similarity_features_df_l.columns))
            features = features.intersection(set(similarity_features_df_r.columns))
            features = sorted(list(features))
            similarity_features_df = similarity_features_df[features]
            similarity_features_df_l = similarity_features_df_l[features]
            similarity_features_df_r = similarity_features_df_r[features]
            similarity_features_lr = (similarity_features_df_l,similarity_features_df_r)
            id_dfs = (id_df, id_df_l, id_df_r)

    true_labels = candset_features_df.gold.values
    if np.sum(true_labels)==0:
        true_labels = None
    
    # Print dataset statistics
    print(f"\nDataset Statistics:")
    print(f"  Total candidate pairs: {len(similarity_features_df):,}")
    print(f"  Number of features: {len(similarity_features_df.columns)}")
    if true_labels is not None:
        pos_count = np.sum(true_labels)
        print(f"  Positive pairs: {pos_count} ({pos_count/len(true_labels)*100:.2f}%)")
    
    # Run zeroER with improved parameters
    # Use paper default c_bay=0.015 and adjustable init_threshold
    print(f"Using init_threshold={init_threshold}, c_bay={c_bay}")
    y_pred = run_zeroer(similarity_features_df, similarity_features_lr,id_dfs,
                        true_labels ,LR_dup_free,LR_identical,run_trans,
                        init_threshold=init_threshold,
                        c_bay=c_bay)
    pred_df = candset_features_df[["ltable_id","rtable_id"]].copy()
    pred_df['pred'] = y_pred
    pred_df.to_csv(join(dataset_path,"pred.csv"))

