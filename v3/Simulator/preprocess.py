import os
import sys
import pandas as pd
import pymysql

this_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(this_dir)
sys.path.append(parent_dir)
from Config import params_config, db_config


def preprocess_datamart(time_diff = 0.000, model_type='tansho', obj_type='one_or_zero'):
    parameters = params_config.parameters
    con = pymysql.connect(**db_config.db_params)
    datamart = _get_data_frame_from_db(
        query_file_path='SqlQuery/extract_data_mart_for_modeling.sql', 
        col_name_list=parameters['DATAFRAME_COL_NAMES']['DATAMART_FOR_MODEL_COLS'],
        con=con
    )
    datamart = _preprocess_target_variable(df=datamart, time_diff=time_diff, model_type=model_type, obj_type=obj_type)
    print('Value count of y: \n', datamart['y'].value_counts())
    print('Value ratio of y: \n', datamart['y'].value_counts() / datamart.shape[0])
    return datamart


def _fetch_all_and_make_list_by(query, con):
    try:
        cursor = con.cursor()
        cursor.execute(query)
        fetch_result = cursor.fetchall()
        fetch_result_list = [item for item in fetch_result]
        cursor.close()
        return fetch_result_list
    except Exception as e:
        print(e)
        

def _read_query(query_file_path):
    with open(query_file_path, 'r', encoding='utf-8') as f:
        query = f.read()
    return query


def _get_data_frame_from_db(query_file_path, col_name_list, con):
    queries = _read_query(query_file_path)
    table_list = _fetch_all_and_make_list_by(queries, con)
    return pd.DataFrame(table_list, columns=col_name_list)


def _define_target_variable(row, time_diff, model_type, obj_type):
    if model_type == 'tansho' and obj_type == 'odds_or_zero':
        if row['arrival_order'] == 1 or row['arrival_sec_diff_from_first'] < time_diff:
            return row['win_odds']
        else:
            return 0
    elif model_type == 'tansho' and obj_type == 'one_or_zero':
        if row['arrival_order'] == 1 or row['arrival_sec_diff_from_first'] < time_diff:
            return 1
        else:
            return 0
    elif model_type == 'fukusho' and obj_type == 'one_or_zero':
        if row['arrival_order'] in [1, 2, 3] or row['arrival_sec_diff_from_first'] < time_diff:
            return 1
        else:
            return 0


def _preprocess_target_variable(df, time_diff, model_type, obj_type):
    df['y'] = df.apply(_define_target_variable, axis=1, time_diff = time_diff, model_type=model_type, obj_type=obj_type)
    print('Model type: ', model_type, '/ Object type: ', obj_type, '\n')
    return df
