parameters = {
    # parameters of scarping URL
    'TARGET_URL_OF_KAIBALAB_RACE': 'https://www.keibalab.jp/db/race/',
    'TARGET_URL_OF_JRA_WIN5': 'http://www.jra.go.jp/dento/info/win5.html',

    # parameters for selenium
    'START_DATE': '19860105',
    'DRIVER_DIR': './chromedriver',
    'PAGE_LOAD_TIMEOUT': 10,
    'RETRIES': 5,
    'RETRIES_WHEN_WEB_CLICK': 3,
    'INITIALIZE_AND_RETRIES': 3,

    # parameters about model training
    'FILE_NAME_OF_HORSE_CATEGORY_ENCODERS': 'Model/files/190805/category_encoded_href_to_the_horse.pkl',
    'FILE_NAME_OF_JOCKEY_CATEGORY_ENCODERS': 'Model/files/190805/category_encoded_href_to_the_jockey.pkl',
    'FILE_NAME_OF_TRAINER_CATEGORY_ENCODERS': 'Model/files/190805/category_encoded_href_to_the_trainer.pkl',
    'HYPER_PARAMETERS': {
        'CATEGORY_ENCODERS_FOR_HORSE': 'TargetEncoder',  # OrdinalEncoder or TargetEncoder
        'CATEGORY_ENCODERS_FOR_JOCKEY': 'TargetEncoder',  # OrdinalEncoder or TargetEncoder
        'CATEGORY_ENCODERS_FOR_TRAINER': 'TargetEncoder',  # OrdinalEncoder or TargetEncoder
        'CATEGORY_ENCODERS_HANDLE_UNKNOWN': 15
    },

    # col names in database tables
    'TABLE_COL_NAMES': {
        'keibalab_race_master': [
            'race_id',
            'race_timing',
            'race_title',
            'race_weather',
            'race_condition',
            'course_syokin_list'
        ],
        'keibalab_race_result_list': [
            'race_id',
            'arrival_order',
            'post_position',
            'horse_number',
            'horse_name',
            'href_to_the_horse',
            'horse_age',
            'horse_weight',
            'horse_impost',
            'jockey_name',
            'href_to_the_jockey',
            'popularity_order',
            'win_odds',
            'trainer_name',
            'href_to_the_trainer'
        ],
        'keibalab_race_prior_info_list': [
            'race_id',
            'post_position',
            'horse_number',
            'horse_name',
            'href_to_the_horse',
            'jockey_name',
            'href_to_the_jockey',
            'trainer_name',
            'horse_age',
            'horse_sex',
            'popularity_order',
            'win_odds',
            'horse_weight',
            'horse_weight_increment_from_previous',
            'owner_name',
            'href_to_the_owner',
            'breeder_name',
            'jockey_finish_first_second',
            'horse_number_finish_first_second',
            'stallion_finish_first_second',
            'conbi_finish_first_second',
            'zensou_info_list'
        ]
    },

    # col names in dataframe
    'DATAFRAME_COL_NAMES': {
        'race_prior_info_for_training': [
            'race_id',
            'race_timing',
            'race_title',
            'race_weather',
            'race_condition',
            'course_syokin_list',
            'post_position',
            'horse_number',
            'href_to_the_horse',
            'horse_sex_age',
            'horse_weight_and_increment',
            'horse_impost',
            'jockey_name',
            'href_to_the_jockey',
            'popularity_order',
            'win_odds',
            'trainer_name',
            'href_to_the_trainer',
            'href_to_the_owner',
            'breeder_name',
            'jockey_finish_first_second',
            'horse_number_finish_first_second',
            'stallion_finish_first_second',
            'conbi_finish_first_second',
            'zensou_info_list',
            'arrival_order'
            ],
        'feature_cols': [
            'year',
            'month',
            'day',
            'dow',
            'race_course_encoded',
            'time_in_the_racecourse',
            'what_day_in_the_racecourse',
            'race_weather_encoded',
            'race_condition_encoded'
            'post_position',
            'horse_number',
            'href_to_the_horse_encoded',
            'horse_age',
            'horse_sex_encoded',
            'horse_weight',
            'horse_weight_increment',
            'horse_impost',
            'weight_loss_encode',
            'href_to_the_jockey_encoded',
            'popularity_order',
            'win_odds',
            'trainer_belonging_encoded',
            'href_to_the_trainer_encoded'
            ],
        'target_col': 'arrival_order'
    }
}
