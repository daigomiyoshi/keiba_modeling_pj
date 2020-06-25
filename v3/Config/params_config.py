parameters = {
    # parameters about scraping netkeiba
    'URL_ABOUT_NETKEIBA': {
        'RACE_TABLE': 'https://race.netkeiba.com/?pid=race_old&id=c',
        'RACE_RESULT': 'https://race.netkeiba.com/?pid=race&id=c{RACE_ID}&mode=result',
        'RACE_PAST5_RESULT': 'https://race.netkeiba.com/?pid=race&id=c{RACE_ID}&mode=shutuba'
    },
    'MIN_YEAR': 2020,
    'MAX_YEAR': 2020,
    'MIN_MONTH': 5,
    'MAX_MONTH': 6,
    'MIN_DATE': 1,
    'MAX_DATE': 31,
    'DRIVER_DIR': 'Config/chromedriver_v83',
    'PAGE_LOAD_TIMEOUT': 10,

    # parameters about columns name of tables
    'TABLE_COL_NAMES': {
        'race_master': [
            'race_id',
            'race_title',
            'race_course',
            'race_weather',
            'race_condition',
            'race_year',
            'race_month',
            'race_date',
            'race_dow',
            'starting_time',
            'race_other_info'
        ],
        'race_table_info': [
            'race_id',
            'bracket_num',
            'horse_num',
            'horse_name',
            'href_to_horse',
            'horse_age',
            'horse_sex',
            'weight_penalty',
            'jockey_name',
            'href_to_jockey',
            'owner_name',
            'href_to_owner',
            'horse_weight',
            'horse_weight_increment',
            'win_odds',
            'popularity_order'
        ],
        'race_result_info': [
            'race_id',
            'bracket_num',
            'horse_num',
            'arrival_time',
            'arrival_diff',
            'arrival_order'
        ],
        'race_refund_info': [
            'race_id',
            'refund_type',
            'groupby_index',
            'horse_num',
            'refund_yen',
            'popularity_order'
        ],
        'race_past_5_result_info': [
            'race_id',
            'bracket_num',
            'horse_num',
            'past_x',
            'past_x_race_title',
            'past_x_race_id',
            'arrival_order'
        ],
        'race_predicted_score': [
            'race_id',
            'horse_num',
            'predicted_score'
        ]
    },

    # parameters about columns names in dataframe
    'DATAFRAME_COL_NAMES': {
        'RACE_MASTER_INFO_COLS': [
            'race_id', 
            'race_place', 
            'race_kai', 
            'race_nichi', 
            'race_round', 
            'race_year', 
            'race_month', 
            'race_date', 
            'race_dow', 
            'race_course_baba', 
            'race_course_distance', 
            'race_course_mawari', 
            'race_weather', 
            'race_condition', 
            'starting_hour', 
            'starting_minutes'
        ],
        'RACE_TABLE_INFO_COLS': [
            'race_id',
            'horse_num',
            'bracket_num',
            'href_to_horse', 
            'horse_age', 
            'horse_sex',
            'weight_penalty',
            'weight_penalty_diff_from_avg',
            'href_to_jockey',
            'href_to_owner',
            'popularity_order',
            'win_odds'
        ],
        'RACE_RESULT_INFO_COLS': [
            'race_id',
            'bracket_num',
            'horse_num',
            'arrival_sec_diff_from_first',
            'arrival_order'
        ],
        'RACE_PAST_5_RACE_INFO_COLS': [
            'race_id',
            'horse_num',
            'count_of_latest_runs',
            'avg_arrival_order',
            'std_arrival_order',
            'latest_arrival_order'
        ]
    }
}
