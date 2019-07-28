parameters = {
    # parameters of scarping URL
    'TARGET_URL_OF_KAIBALAB_RACE': 'https://www.keibalab.jp/db/race/',
    'TARGET_URL_OF_JRA_WIN5': 'http://www.jra.go.jp/dento/info/win5.html',

    # parameters of selenium
    'START_DATE': '19860105',
    'DRIVER_DIR': "./chromedriver",
    'PAGE_LOAD_TIMEOUT': 10,
    'RETRIES': 5,
    'RETRIES_WHEN_WEB_CLICK': 3,
    'INITIALIZE_AND_RETRIES': 3,

    # col names in database tables
    'TABLE_COL_NAMES': {
        'keibalab_race_master': ['race_id',
                                 'race_timing',
                                 'race_title',
                                 'race_weather',
                                 'race_condition',
                                 'course_syokin_list'],
        'keibalab_race_result_list': ['race_id',
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
                                      'href_to_the_trainer'],
        'keibalab_race_prior_info_list': ['race_id',
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
                                          'zensou_info_list']
    }
}
