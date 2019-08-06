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

    race_prior_info_list_trained = get_race_prior_info_list_for_training(queries, con)
    race_prior_info_df_trained = pd.DataFrame(race_prior_info_list_trained,
                                              columns=parameters['DATAFRAME_COL_NAMES']['race_prior_info_for_training'])

    print('Preprocessing the train data')
    pp = Preprocessing(parameters)
    race_prior_info_df_trained = preprocess_race_prior_info_df(race_prior_info_df_trained, pp)

    print('Fit the train data into the model')


def preprocess_race_prior_info_df(df, pp):
    df = pp.preprocess_race_timing(df)
    df = pp.encode_race_weather(df)
    df = pp.encode_race_condition(df)
    df = pp.encode_fit_and_transform_href_to_the_horse(df)
    df = pp.preprocess_horse_sex_age(df)
    df = pp.preprocess_horse_weight_and_increment(df)
    df = pp.preprocess_jockey_name(df)
    df = pp.encode_fit_and_transform_href_to_the_jockey(df)
    df = pp.preprocess_trainer_name(df)
    df = pp.encode_fit_and_transform_href_to_the_trainer(df)
    return df


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


def get_race_prior_info_list_for_training(queries, con):
    selected_query = queries['RACE_PRIOR_INFO_FOR_TRAINING']
    return fetchall_and_make_list_by(selected_query, con)


if __name__ == '__main__':
    main()
