import pymysql
import pandas as pd

from Config import params_config, query_config, db_config
from Model.Preprocessing import Preprocessing

import warnings
warnings.filterwarnings('ignore')


def main():
    parameters = params_config.parameters
    queries = query_config.queries
    db_params = db_config.db_params
    con = pymysql.connect(**db_params)

    print('Extracting the train data')
    training_race_df = get_training_race_data_frame(queries, parameters, con)

    print('Preprocessing the train data')
    pp = Preprocessing(parameters)
    training_race_df_preprocessed = preprocess_result_data_based_training_race_df(training_race_df, pp)

    print('Fit the train data into the model')


def fetchall_and_make_list_by(query, con):
    try:
        cursor = con.cursor()
        cursor.execute(query)
        fetch_result = cursor.fetchall()
        fetch_result_list = [item for item in fetch_result]
        cursor.close()
        return fetch_result_list
    except Exception as e:
        print(e)


def get_training_race_data_frame(queries, parameters, con):
    selected_query = queries['TRAINING_DATA_FROM_MASTER_PRIOR_RESULT']
    training_race_data_list = fetchall_and_make_list_by(selected_query, con)
    training_race_data_frame = pd.DataFrame(training_race_data_list,
                                            columns=parameters['DATAFRAME_COL_NAMES']['training_race_data_cols'])
    return training_race_data_frame


def preprocess_result_data_based_training_race_df(df, pp):
    df = pp.preprocess_race_timing(df=df)
    df = pp.encode_race_weather(df=df)
    df = pp.encode_race_condition(df=df)
    df = pp.encode_fit_and_transform_href_to_the_horse(df=df)
    df = pp.preprocess_horse_sex_age(df=df, target_cols_type='result')
    df = pp.preprocess_horse_weight_and_increment(df=df, target_cols_type='result')
    df = pp.preprocess_jockey_name(df=df, target_cols_type='result')
    df = pp.encode_fit_and_transform_href_to_the_jockey(df=df)
    df = pp.preprocess_trainer_name(df=df, target_cols_type='result')
    df = pp.preprocess_arrival_order(df=df)
    return df


if __name__ == '__main__':
    main()
