import os
import sys
import pandas as pd
import joblib
import h2o
from h2o.automl import H2OAutoML

this_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(this_dir)
sys.path.append(parent_dir)
from Config import params_config


def fit(datamart):
    parameters = params_config.parameters
    Idx_train, X_train, y_train, Idx_test, X_test, y_test = make_train_test_data(
        parameters=parameters, dataset=datamart, how_to_select='include'
    )
    y_test_pred = fit_model_into_data_by(
        parameters=parameters,
        model_type='h2o_clf',
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test
    )
    return y_test_pred


def make_train_test_data(parameters, dataset, how_to_select):
    index_cols = parameters['TRAIN_TEST_SPLIT']['INDEX_COL']
    if how_to_select == 'include':
        feature_cols = parameters['TRAIN_TEST_SPLIT']['FEATURE_COLS']
    elif how_to_select == 'exclude':
        feature_cols = [col for col in list(dataset.columns) if col not in parameters['TRAIN_TEST_SPLIT']['EXCLUDE_COL']]
    print('Feature cols used are:', feature_cols, '\n')
    target_col = parameters['TRAIN_TEST_SPLIT']['TARGET_COL']
    criteria_to_split_dict = parameters['TRAIN_TEST_SPLIT']['CRITERIA_TO_SPLIT_DATA']
    
    train_df = pd.DataFrame()
    train_df = pd.concat([train_df, dataset[dataset['race_year'] < criteria_to_split_dict['race_year']]])
    train_df = pd.concat([train_df, dataset[
        (dataset['race_year'] == criteria_to_split_dict['race_year']) & 
        (dataset['race_month'] <= criteria_to_split_dict['race_month'])
    ]])
    Idx_train = train_df[index_cols]
    X_train = train_df[feature_cols]
    y_train = train_df[target_col]
    
    test_df = pd.DataFrame()
    test_df = pd.concat([test_df, dataset[dataset['race_year'] > criteria_to_split_dict['race_year']]])
    test_df = pd.concat([test_df, dataset[
        (dataset['race_year'] == criteria_to_split_dict['race_year']) & 
        (dataset['race_month'] > criteria_to_split_dict['race_month'])
    ]])
    Idx_test = test_df[index_cols]
    X_test = test_df[feature_cols]
    y_test = test_df[target_col]

    return Idx_train, X_train, y_train, Idx_test, X_test, y_test


def fit_model_into_data_by(parameters, model_type, X_train, X_test, y_train, y_test):
    if model_type == 'h2o_reg' or model_type == 'h2o_clf':
        x=list(X_train.columns)
        y=parameters['TRAIN_TEST_SPLIT']['TARGET_COL']
        h2o.init(ip="127.0.0.1", max_mem_size_GB=4)
        hdf = h2o.H2OFrame(pd.concat([X_train, y_train], axis=1))
        
        if model_type == 'h2o_clf':
            hdf[y] = hdf[y].asfactor()
        
        aml = H2OAutoML(max_models=10, seed=1, max_runtime_secs=432000)
        aml.train(
            x=list(X_train.columns),
            y=parameters['TRAIN_TEST_SPLIT']['TARGET_COL'],
            training_frame=hdf
        )
        lb = aml.leaderboard
        print(lb.head(rows=lb.nrows))
        model_path = h2o.save_model(
            model=aml.leader,
            path=parameters['DIR_NAME_OF_MODEL_PICKLE']+'fitted_'+model_type+'_model',
            force=True
        )
        print('Save the fitted model, the path is:', model_path, '. \n')
        saved_model = h2o.load_model(model_path)
        y_test_pred = saved_model.predict(h2o.H2OFrame(X_test)).as_data_frame()
        
    elif model_type == 'rf':
        pass

    return y_test_pred
