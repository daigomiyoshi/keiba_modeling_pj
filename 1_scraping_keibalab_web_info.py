import time
import datetime
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, InvalidSessionIdException

from Config import params_config, db_config
from ScrapingTools.KeibaLabRaceInfoScraper import RaceInfoScraper
from ScrapingTools.KeibaLabHorseInfoScraper import HorseInfoScraper

import warnings
warnings.filterwarnings('ignore')


def main():
    parameters = params_config.parameters
    db_params = db_config.db_params
    driver = initialize_chrome_driver(parameters)

    ris = RaceInfoScraper(driver, parameters, db_params)
    scraping_race_info_until_start_date(driver, parameters, db_params, ris)
    driver.close()
    print('Finish scraping.')

    # his = HorseInfoScraper(driver, parameters, db_params)
    # driver = initialize_chrome_driver(parameters)
    # scraping_horse_info_not_acquired(driver, parameters, db_params, his)

    driver.quit()


def initialize_chrome_driver(parameters):
    chrome_options = Options()
    chrome_options.add_argument('--dns-prefetch-disable')
    driver = Chrome(executable_path=parameters['DRIVER_DIR'], chrome_options=chrome_options)
    driver.set_page_load_timeout(parameters['PAGE_LOAD_TIMEOUT'])
    driver.maximize_window()
    return driver


# Functions for scraping_race_info_until_start_date
def get_nearest_future_holidays_list():
    target_datetime = datetime.date.today()
    target_datetime = datetime.date(2015, 9, 20)
    if target_datetime.weekday() == 6:
        sunday_datetime_str = target_datetime.strftime("%Y%m%d")
        target_datetime_minus_1 = target_datetime + datetime.timedelta(days=-1)
        saturday_datetime_str = target_datetime_minus_1.strftime("%Y%m%d")
        return [saturday_datetime_str, sunday_datetime_str]

    while True:
        if target_datetime.weekday() == 5:
            saturday_datetime_str = target_datetime.strftime("%Y%m%d")
            target_datetime_plus_1 = target_datetime + datetime.timedelta(days=1)
            sunday_datetime_str = target_datetime_plus_1.strftime("%Y%m%d")
            return [saturday_datetime_str, sunday_datetime_str]
        else:
            target_datetime = target_datetime + datetime.timedelta(days=1)


def get_latest_holidays_list(target_datetime):
    while True:
        if target_datetime.weekday() == 5:
            saturday_datetime_str = target_datetime.strftime("%Y%m%d")
            target_datetime_plus_1 = target_datetime + datetime.timedelta(days=1)
            sunday_datetime_str = target_datetime_plus_1.strftime("%Y%m%d")
            return [saturday_datetime_str, sunday_datetime_str]
        else:
            target_datetime = target_datetime + datetime.timedelta(days=-1)


def try_scraping_info_in(driver, parameters, db_params, ris, target_datetime_str):
    for i in range(parameters['INITIALIZE_AND_RETRIES']):
        try:
            ris.scraping_race_info_in(target_datetime_str)
        except (NoSuchElementException, TimeoutException, InvalidSessionIdException,
                ConnectionRefusedError, IndexError):
            print('Timeout or Error, so initializing driver and retry... ({TIME}/{MAX})'.
                  format(TIME=i + 1, MAX=parameters['INITIALIZE_AND_RETRIES']))
            driver.close()
            del driver
            time.sleep(5)
            driver = initialize_chrome_driver(parameters)
            ris = RaceInfoScraper(driver, parameters, db_params)
            continue
        else:
            print('scraped the web site info in {TARGET_DATE}'.format(TARGET_DATE=target_datetime_str))
            print()
            return True
    print('Failed to scrape the web site info in {TARGET_DATE}'.format(TARGET_DATE=target_datetime_str))
    print()
    return None


def scraping_race_info_until_start_date(driver, parameters, db_params, ris):
    # scarping nearest future days web info at first time
    target_datetime_list = get_nearest_future_holidays_list()
    for target_datetime_str in reversed(target_datetime_list):
        try_scraping_info_in(driver, parameters, db_params, ris, target_datetime_str)

    # after the second time, scraping the past holidays web info
    while True:
        target_datetime = datetime.datetime.strptime(target_datetime_list[0], '%Y%m%d') - datetime.timedelta(days=1)
        target_datetime_list = get_latest_holidays_list(target_datetime)

        for target_datetime_str in reversed(target_datetime_list):
            try_scraping_info_in(driver, parameters, db_params, ris, target_datetime_str)

        if parameters['START_DATE'] in target_datetime_list:
            break


# Functions for scraping_horse_info_not_acquired
def scraping_horse_info_not_acquired(driver, parameters, db_params, his):
    pass


if __name__ == '__main__':
    main()
