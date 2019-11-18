model_params = {
    'CATEGORICAL_FEATURES_DICT': {
        'race_place': 'OrdinalEncoder',
        'race_corse_baba': 'OrdinalEncoder',
        'race_corse_mawari': 'OrdinalEncoder',
        'race_weather': 'OrdinalEncoder',
        'race_condition': 'OrdinalEncoder',
        'race_dow': 'OrdinalEncoder',

        'href_to_horse': 'LeaveOneOutEncoder',
        'horse_sex': 'OrdinalEncoder',
        'href_to_jockey': 'LeaveOneOutEncoder',
        'href_to_owner': 'LeaveOneOutEncoder'
    },

    'FEATURETOOLS_PARAMS': {
        'INDEX_COL': {
            'RACE_MASTER': ['race_id'],
            'RACE_TABLE_RESULT': ['race_id', 'race_horse_id'],
            'RACE_PAST_X_RESULT': ['race_horse_id', 'race_horse_past_x_id']
        },
        'FEATURE_COL': {
            'RACE_MASTER': [
                'race_round',
                'race_kai',
                'race_place',
                'race_corse_baba',
                'race_corse_dist',
                'race_corse_mawari',
                'race_weather',
                'race_condition',
                'race_year',
                'race_month',
                'race_date',
                'race_dow',
                'starting_hour',
                'starting_minutes'
            ],
            'RACE_TABLE_RESULT': [
                'bracket_num',
                'href_to_horse',
                'horse_age',
                'horse_sex',
                'weight_penalty',
                'href_to_jockey',
                'href_to_owner',
                'popularity_order',
                'win_odds'
            ],
            'RACE_PAST_X_RESULT': [
                'past_x_arrival_order',
                'arrival_sec_diff_from_first'
            ]
        },
        'PRIMITIVES': {
            'aggregation': ['sum', 'mean', 'std', 'max', 'min', 'count', 'skew'],
            'transform': []
        }
    },

    'TRAIN_TEST_SPLIT': {
        'INDEX_COL': ['race_id', 'horse_num'],
        'EXCLUDE_COL': ['race_id', 'horse_num', 'y'],
        'TARGET_COL': 'y',
        'CRITERIA_TO_SPLIT_DATA': {'race_master.race_year': 2019, 'race_master.race_month': 3}
    }

}