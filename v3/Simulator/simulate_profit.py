import os
import sys
import pandas as pd

this_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(this_dir)
sys.path.append(parent_dir)
from Config import params_config


def make_test_dataset(Idx_test, y_test_pred, y_test, model_type):
    Idx_test = Idx_test.reset_index(drop=True)
    y_test = y_test.reset_index(drop=True)
    
    if model_type == 'clf':
        y_pred_proba = pd.DataFrame({'y_pred_proba': y_test_pred['p1']})
        y_pred_proba = y_pred_proba.reset_index(drop=True)
    elif model_type == 'reg':
        pass
    
    return pd.concat([pd.concat([Idx_test, y_pred_proba], axis=1), y_test], axis=1)
