
parameters = {

    # parameters for scraping

    'TARGET_URL': 'https://race.netkeiba.com/?pid=schedule&select=schedule&year={YEAR}',
    'YEAR_RANGE': range(2002, 2019+1),
    'DRIVER_MAC': "./chromedriver",
    'PAGE_LOAD_TIMEOUT': 10
    # 'INTERVAL': 3
}