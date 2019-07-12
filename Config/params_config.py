parameters = {
    # parameters for scraping

    # 'TARGET_URL': 'https://race.netkeiba.com/?pid=schedule&select=schedule&year={YEAR}',
    # 'YEAR_RANGE': range(2002, 2019+1),

    'TARGET_URL': 'https://www.keibalab.jp/db/race/',
    'START_DATE': '19860105',  # sunday
    'DRIVER_DIR': "./chromedriver",
    'PAGE_LOAD_TIMEOUT': 10,
    'RETRIES': 3,

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
                                      'href_to_the_trainer']
    }
}
