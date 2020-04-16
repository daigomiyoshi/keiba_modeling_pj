import pymysql
import re
import pandas as pd
import numpy as np
import category_encoders as ce
import featuretools as ft
import joblib
import h2o
from h2o.automl import H2OAutoML
from boruta import BorutaPy
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

from Utils.bulk_insert import BulkInsert
from Config import params_config, db_config, queries_config, model_params_config

import warnings
warnings.filterwarnings('ignore')


def main():
    con = pymysql.connect(**db_config.db_params)
    parameters = params_config.parameters
    model_params = model_params_config.model_params
    queries = queries_config.queries

    print('Get and preprocess race table info')
    race_master_df = _get_race_master_data_frame(queries, parameters, con)
    race_table_result_df = _get_race_table_result_data_frame(queries, parameters, con)
    race_table_result_df = preprocess_race_table_result_df_idx(race_table_result_df)
    race_table_result_df = preprocess_target_variable(race_table_result_df)
    race_past_x_result_df = _get_race_past_x_result_data_frame(queries, parameters, con)
    race_past_x_result_df = preprocess_race_past_x_result_df_idx(race_past_x_result_df)

    race_master_df = encode_category_variables(race_master_df, model_params)
    race_table_result_df = encode_category_variables(race_table_result_df, model_params)
    race_past_x_result_df = encode_category_variables(race_past_x_result_df, model_params)

    print('Auto feature engineering')
    feature_matrix_df, table_index_df = engineer_features_by_featuretools(
        model_params, race_master_df, race_table_result_df, race_past_x_result_df
    )

    print('Split Train Test data')
    Idx_train, X_train, y_train, Idx_test, X_test, y_test = make_train_test_data(
        feature_matrix_df, race_table_result_df, table_index_df, model_params
    )

    print('Auto feature selection')
    feature_selected_cols, X_train_selected, X_test_selected = select_features_by_boruta(X_train, X_test, y_train)

    print('Auto supervised learning')

    y_test_pred = fit_model_into_data_by(model_type='h2o',
                                         features='selected',
                                         model_params=model_params,
                                         X_train=X_train,
                                         X_test=X_test,
                                         X_train_selected=X_train_selected,
                                         X_test_selected=X_test_selected,
                                         y_train=y_train,
                                         y_test=y_test)

    print('Finish modeling, and insert predicted score into database')
    con = pymysql.connect(**db_config.db_params)
    predicted_score_df = pd.concat(
        [Idx_test.reset_index(drop=True), pd.DataFrame(np.round(y_test_pred, 3), columns=['predicted_score'])], axis=1
    )
    predicted_score_list = predicted_score_df.values.tolist()
    _bulk_insert(con, predicted_score_list, 'race_predicted_score', parameters['TABLE_COL_NAMES']['race_predicted_score'])

    print('Finish.')


def _fetchall_and_make_list_by(query, con):
    try:
        cursor = con.cursor()
        cursor.execute(query)
        fetch_result = cursor.fetchall()
        fetch_result_list = [item for item in fetch_result]
        cursor.close()
        return fetch_result_list
    except Exception as e:
        print(e)


def _get_race_master_data_frame(queries, parameters, con):
    race_master_list = _fetchall_and_make_list_by(queries['RACE_MASTER_INFO'], con)
    return pd.DataFrame(race_master_list, columns=parameters['DATAFRAME_COL_NAMES']['RACE_MASTER_INFO_COLS'])


def _get_race_table_result_data_frame(queries, parameters, con):
    race_table_result_list = _fetchall_and_make_list_by(queries['RACE_TABLE_RESULT_INFO'], con)
    return pd.DataFrame(race_table_result_list, columns=parameters['DATAFRAME_COL_NAMES']['RACE_TABLE_RESULT_INFO_COLS'])


def _get_race_past_x_result_data_frame(queries, parameters, con):
    race_past_x_result_list = _fetchall_and_make_list_by(queries['RACE_PAST_X_RESULT_INFO'], con)
    return pd.DataFrame(race_past_x_result_list, columns=parameters['DATAFRAME_COL_NAMES']['RACE_PAST_X_RESULT_INFO_COLS'])


def _make_race_horse_id(row):
    horse_num_str = str(row['horse_num']) if row['horse_num'] >= 10 else '0' + str(row['horse_num'])
    return row['race_id'] + '_' + horse_num_str


def preprocess_race_table_result_df_idx(df):
    df['race_horse_id']= df.apply(_make_race_horse_id, axis=1)
    return df


def _make_race_horse_past_x_id(row):
    horse_num_str = str(row['horse_num']) if row['horse_num'] >= 10 else '0' + str(row['horse_num'])
    return row['race_id'] + '_' + horse_num_str + '_' + str(row['past_x'])


def preprocess_race_past_x_result_df_idx(df):
    df['race_horse_id']= df.apply(_make_race_horse_id, axis=1)
    df['race_horse_past_x_id']= df.apply(_make_race_horse_past_x_id, axis=1)
    return df


def _define_target_variable(row, model_type='win', obj_type='odds_or_zero'):
    if model_type == 'win' and obj_type == 'odds_or_zero':
        if row['arrival_order'] == 1 or row['arrival_sec_diff_from_first'] <= 0.002:
            return row['win_odds']
        else:
            return 0


def preprocess_target_variable(df):
    df['y'] = df.apply(_define_target_variable, axis=1, model_type='win', obj_type='odds_or_zero')
    return df


def encode_category_variables(df, model_params):
    for key, value in model_params['CATEGORICAL_FEATURES_DICT'].items():
        if key not in df.columns:
            continue
        if value == 'OrdinalEncoder':
            ce_oe = ce.OrdinalEncoder(cols=key, handle_unknown='impute')
            df = ce_oe.fit_transform(df)
        elif value == 'OneHotEncoder':
            ce_ohe = ce.OneHotEncoder(cols=key, handle_unknown='impute')
            df = ce_ohe.fit_transform(df)
        elif value == 'LeaveOneOutEncoder':
            ce_looe = ce.LeaveOneOutEncoder(cols=key, handle_unknown='impute')
            df = ce_looe.fit_transform(df, y=df[model_params['CATEGORICAL_FEATURES_DICT']['target_y']])
    return df


def decode_race_horse_id(feature_matrix_df):
    def get_race_id(row):
        race_id = re.split('_', row['race_horse_id'])[0]
        return race_id

    def get_horse_num(row):
        horse_num = int(re.split('_', row['race_horse_id'])[1])
        return horse_num

    table_index_df = pd.DataFrame()
    table_index_df['race_id'] = pd.DataFrame(feature_matrix_df.index).apply(get_race_id, axis=1)
    table_index_df['horse_num'] = pd.DataFrame(feature_matrix_df.index).apply(get_horse_num, axis=1)
    return table_index_df


def engineer_features_by_featuretools(model_params, race_master_df, race_table_result_df, race_past_x_result_df):
    es = ft.EntitySet(id='netkeiba')
    es.entity_from_dataframe(entity_id='race_master',
                             dataframe=race_master_df[model_params['FEATURETOOLS_PARAMS']['INDEX_COL']['RACE_MASTER'] +
                                                      model_params['FEATURETOOLS_PARAMS']['FEATURE_COL'][
                                                          'RACE_MASTER']],
                             index='race_id')
    es.entity_from_dataframe(entity_id='race_table',
                             dataframe=race_table_result_df[
                                 model_params['FEATURETOOLS_PARAMS']['INDEX_COL']['RACE_TABLE_RESULT'] +
                                 model_params['FEATURETOOLS_PARAMS']['FEATURE_COL']['RACE_TABLE_RESULT']],
                             index='race_horse_id')
    es.entity_from_dataframe(entity_id='race_past_x',
                             dataframe=race_past_x_result_df[
                                 model_params['FEATURETOOLS_PARAMS']['INDEX_COL']['RACE_PAST_X_RESULT'] +
                                 model_params['FEATURETOOLS_PARAMS']['FEATURE_COL']['RACE_PAST_X_RESULT']],
                             index='race_horse_past_x_id')

    r_master_table = ft.Relationship(es['race_master']['race_id'], es['race_table']['race_id'])
    r_table_past_x = ft.Relationship(es['race_table']['race_horse_id'], es['race_past_x']['race_horse_id'])

    es.add_relationships(relationships=[r_master_table])
    es.add_relationships(relationships=[r_table_past_x])

    feature_matrix_df, _ = ft.dfs(
        entityset=es,
        target_entity='race_table',
        agg_primitives=model_params['FEATURETOOLS_PARAMS']['PRIMITIVES']['aggregation'],
        trans_primitives=model_params['FEATURETOOLS_PARAMS']['PRIMITIVES']['transform'],
        max_depth=2
    )
    feature_matrix_df = feature_matrix_df.fillna(0)
    table_index_df = decode_race_horse_id(feature_matrix_df)
    feature_matrix_df = feature_matrix_df.reset_index(drop=True)
    return feature_matrix_df, table_index_df


def make_train_test_data(feature_df, y_df, idx_df, model_params):
    dataset = pd.concat([feature_df, y_df[model_params['TRAIN_TEST_SPLIT']['TARGET_COL']]], axis='columns')
    dataset = pd.concat([idx_df, dataset], axis='columns')

    index_cols = model_params['TRAIN_TEST_SPLIT']['INDEX_COL']
    feature_cols = [col for col in list(dataset.columns) if col not in model_params['TRAIN_TEST_SPLIT']['EXCLUDE_COL']]
    target_col = model_params['TRAIN_TEST_SPLIT']['TARGET_COL']
    criteria_to_split_dict = model_params['TRAIN_TEST_SPLIT']['CRITERIA_TO_SPLIT_DATA']

    Idx_train = dataset[
        (dataset[list(criteria_to_split_dict)[0]] < criteria_to_split_dict[list(criteria_to_split_dict)[0]]) |
        (dataset[list(criteria_to_split_dict)[1]] < criteria_to_split_dict[list(criteria_to_split_dict)[1]])
        ][index_cols]
    Idx_train = Idx_train.loc[:, ~Idx_train.columns.duplicated()]

    X_train = dataset[
        (dataset[list(criteria_to_split_dict)[0]] < criteria_to_split_dict[list(criteria_to_split_dict)[0]]) |
        (dataset[list(criteria_to_split_dict)[1]] < criteria_to_split_dict[list(criteria_to_split_dict)[1]])
        ][feature_cols]

    y_train = dataset[
        (dataset[list(criteria_to_split_dict)[0]] < criteria_to_split_dict[list(criteria_to_split_dict)[0]]) |
        (dataset[list(criteria_to_split_dict)[1]] < criteria_to_split_dict[list(criteria_to_split_dict)[1]])
        ][target_col]

    Idx_test = dataset[
        (dataset[list(criteria_to_split_dict)[0]] >= criteria_to_split_dict[list(criteria_to_split_dict)[0]]) &
        (dataset[list(criteria_to_split_dict)[1]] >= criteria_to_split_dict[list(criteria_to_split_dict)[1]])
        ][index_cols]
    Idx_test = Idx_test.loc[:, ~Idx_test.columns.duplicated()]

    X_test = dataset[
        (dataset[list(criteria_to_split_dict)[0]] >= criteria_to_split_dict[list(criteria_to_split_dict)[0]]) &
        (dataset[list(criteria_to_split_dict)[1]] >= criteria_to_split_dict[list(criteria_to_split_dict)[1]])
        ][feature_cols]

    y_test = dataset[
        (dataset[list(criteria_to_split_dict)[0]] >= criteria_to_split_dict[list(criteria_to_split_dict)[0]]) &
        (dataset[list(criteria_to_split_dict)[1]] >= criteria_to_split_dict[list(criteria_to_split_dict)[1]])
        ][target_col]

    return Idx_train, X_train, y_train, Idx_test, X_test, y_test


def select_features_by_boruta(X_train, X_test, y_train):
    model = RandomForestRegressor(
        n_estimators=50,
        max_depth=5,
        max_features='sqrt',
        n_jobs=-1,
        verbose=True,
        random_state=1
    )

    features_selector = BorutaPy(
        model,
        n_estimators='auto',
        perc=80,
        verbose=2,
        two_step=False,
        max_iter=100,
        random_state=1
    )

    features_selector.fit(X_train.values, y_train.values)
    X_train_selected = X_train.iloc[:, features_selector.support_]
    X_test_selected = X_test.iloc[:, features_selector.support_]
    feature_selected_cols = list(X_train_selected.columns)
    print('Selected features are: ', feature_selected_cols)

    return feature_selected_cols, X_train_selected, X_test_selected


def fit_model_into_data_by(model_type, features,
                           model_params, X_train, X_test, X_train_selected, X_test_selected, y_train, y_test):
    if features == 'all':
        feature_cols = [col for col in list(X_train.columns) if
                        col not in model_params['TRAIN_TEST_SPLIT']['EXCLUDE_COL']]
        train = X_train
        test = X_test
    elif features == 'selected':
        feature_cols = [col for col in list(X_train_selected.columns) if
                        col not in model_params['TRAIN_TEST_SPLIT']['EXCLUDE_COL']]
        train = X_train_selected
        test = X_test_selected
    target_col = model_params['TRAIN_TEST_SPLIT']['TARGET_COL']

    if model_type == 'h2o':
        h2o.init(ip="127.0.0.1", max_mem_size_GB=2)
        hdf = h2o.H2OFrame(pd.concat([train, y_train], axis=1))
        aml = H2OAutoML(max_models=5, seed=1, max_runtime_secs=432000)
        aml.train(
            x=feature_cols,
            y=target_col,
            training_frame=hdf
        )
        h2o.save_model(model=aml,
                       path=model_params['DIR_NAME_OF_MODEL_PICKLE']+'fitted_'+features+'_features_'+model_type+'_model',
                       force=True)
        # joblib.dump(aml,
        #             model_params['DIR_NAME_OF_MODEL_PICKLE']+'fitted_'+features+'_features_'+model_type+'_model.pkl')
        y_test_pred = aml.predict(h2o.H2OFrame(test)).as_data_frame()['predict']
    elif model_type == 'rf':
        rf_reg = RandomForestRegressor(
            n_estimators=1000,
            max_depth=10,
            max_features='sqrt',
            n_jobs=-1,
            verbose=1,
            random_state=1
        )
        rf_reg.fit(train, y_train)
        joblib.dump(rf_reg, model_params['DIR_NAME_OF_MODEL_PICKLE']+'fitted_'+features+'_features_'+model_type+'_model.pkl')
        y_test_pred = rf_reg.predict(test)

    print('RMSE: ', np.sqrt(mean_squared_error(y_test_pred, y_test)))
    print('R2: ', r2_score(y_test_pred, y_test))
    return y_test_pred


def _bulk_insert(con, insert_list, target_table_name, insert_col_names):
    try:
        bi = BulkInsert(con)
        bi.execute(insert_data=insert_list, target_table=target_table_name, col_names=insert_col_names)
    except RuntimeError as e:
        print(e)
        raise TypeError


if __name__ == '__main__':
    main()
