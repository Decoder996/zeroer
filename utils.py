import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score

from model import get_y_init_given_threshold,ZeroerModel

DEL = 1e-300


def get_results(true_labels, predicted_labels):
    p = precision_score(true_labels, predicted_labels)
    r = recall_score(true_labels, predicted_labels)
    f1 = f1_score(true_labels, predicted_labels)
    return p, r, f1


def run_zeroer(similarity_features_df, similarity_features_lr,id_dfs,true_labels,LR_dup_free,LR_identical,run_trans, init_threshold=0.8, c_bay=0.015):
    # Check and normalize features if needed
    from sklearn.preprocessing import MinMaxScaler
    feature_min = similarity_features_df.min().min()
    feature_max = similarity_features_df.max().max()
    
    if feature_min < 0 or feature_max > 1:
        print(f"Warning: Features are not in [0,1] range (min={feature_min:.4f}, max={feature_max:.4f})")
        print("Normalizing features to [0,1] range...")
        scaler = MinMaxScaler()
        similarity_features_df = pd.DataFrame(
            scaler.fit_transform(similarity_features_df),
            columns=similarity_features_df.columns,
            index=similarity_features_df.index
        )
        print("Features normalized successfully.")
    else:
        print(f"Features are in valid range [0,1] (min={feature_min:.4f}, max={feature_max:.4f})")
    
    similarity_matrix = similarity_features_df.values
    y_init = get_y_init_given_threshold(similarity_features_df, threshold=init_threshold)
    
    # Print initialization statistics
    init_positive = sum(y_init)
    init_negative = len(y_init) - init_positive
    print(f"Initialization: {init_positive} positive ({init_positive/len(y_init)*100:.2f}%), {init_negative} negative ({init_negative/len(y_init)*100:.2f}%)")
    
    similarity_matrixs = [similarity_matrix,None,None]
    y_inits = [y_init,None,None]
    if similarity_features_lr[0] is not None:
        # Normalize left-right features if needed
        normalized_lr = []
        for i, lr_df in enumerate(similarity_features_lr):
            if lr_df is not None:
                lr_min = lr_df.min().min()
                lr_max = lr_df.max().max()
                if lr_min < 0 or lr_max > 1:
                    print(f"Normalizing similarity_features_lr[{i}]...")
                    scaler = MinMaxScaler()
                    normalized_df = pd.DataFrame(
                        scaler.fit_transform(lr_df),
                        columns=lr_df.columns,
                        index=lr_df.index
                    )
                    normalized_lr.append(normalized_df)
                else:
                    normalized_lr.append(lr_df)
            else:
                normalized_lr.append(None)
        
        similarity_matrixs[1] = normalized_lr[0].values
        similarity_matrixs[2] = normalized_lr[1].values
        y_inits[1] = get_y_init_given_threshold(normalized_lr[0], threshold=init_threshold)
        y_inits[2] = get_y_init_given_threshold(normalized_lr[1], threshold=init_threshold)
    feature_names = similarity_features_df.columns

    print(f"Using c_bay={c_bay} (paper default: 0.015)")
    model, y_pred = ZeroerModel.run_em(similarity_matrixs, feature_names, y_inits,id_dfs,LR_dup_free,LR_identical, run_trans, y_true=true_labels,
                                       hard=False, c_bay=c_bay)
    if true_labels is not None:
        p, r, f1 = get_results(true_labels, np.round(np.clip(y_pred + DEL, 0., 1.)).astype(int))
        print("Results after EM:")
        print("F1: {:0.2f}, Precision: {:0.2f}, Recall: {:0.2f}".format(f1, p, r))
    return y_pred
