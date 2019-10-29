parameters = {

    # parameters about scraping
    'URL_ABOUT_NETKEIBA': {
        'RACE_TABLE': 'https://race.netkeiba.com/?pid=race_old&id=c',
        'RACE_RESULT': 'https://race.netkeiba.com/?pid=race&id=c{RACE_ID}&mode=result'
    },

    # parameters about model training

    # col names in database tables
    'TABLE_COL_NAMES': {
        'race_master': [
            'race_id',
            'race_title',
            'race_coure',
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
        ]
    },

    # col names in dataframe
    'DATAFRAME_COL_NAMES': {

    }
}