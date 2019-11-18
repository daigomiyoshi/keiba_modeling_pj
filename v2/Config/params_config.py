parameters = {

    # parameters about scraping
    'URL_ABOUT_NETKEIBA': {
        'RACE_TABLE': 'https://race.netkeiba.com/?pid=race_old&id=c',
        'RACE_RESULT': 'https://race.netkeiba.com/?pid=race&id=c{RACE_ID}&mode=result',
        'RACE_PAST5_RESULT': 'https://race.netkeiba.com/?pid=race&id=c{RACE_ID}&mode=shutuba'
    },
    'LATEST_YEAR': 2019,

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
            'race_info_1',
            'race_info_2',
            'race_info_3'
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

    # col names in dataframe
    'DATAFRAME_COL_NAMES': {
        'RACE_MASTER_INFO_COLS': [
            'race_id',
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
        'RACE_TABLE_RESULT_INFO_COLS': [
            'race_id',
            'horse_num',
            'bracket_num',
            'href_to_horse',
            'horse_age',
            'horse_sex',
            'weight_penalty',
            'href_to_jockey',
            'href_to_owner',
            'popularity_order',
            'win_odds',
            'arrival_sec_diff_from_first',
            'arrival_order'
        ],
        'RACE_PAST_X_RESULT_INFO_COLS': [
            'race_id',
            'horse_num',
            'past_x',
            'past_x_arrival_order',
            'arrival_sec_diff_from_first'
        ]
    }
}
