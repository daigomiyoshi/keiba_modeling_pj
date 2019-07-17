import datetime
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from Config import params_config, db_config
from ScrapingTools.KeibaLabScraper import KeibaLabScraper

import warnings
warnings.filterwarnings('ignore')


def main():
    parameters = params_config.parameters
    db_params = db_config.db_params
    driver = initialize_chrome_driver(parameters)
    kls = KeibaLabScraper(driver, parameters, db_params)

    scraping_race_info_until_start_date(parameters, kls)

    driver.quit()


def initialize_chrome_driver(parameters):
    driver = webdriver.Chrome(executable_path=parameters['DRIVER_DIR'])
    driver.set_page_load_timeout(parameters['PAGE_LOAD_TIMEOUT'])
    driver.maximize_window()
    return driver


def get_nearest_future_holidays_list():
    target_datetime = datetime.date.today()
    target_datetime = datetime.date(2019, 6, 2)
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


def try_scraping_info_in(parameters, kls, target_datetime_str):
    for i in range(parameters['RETRIES']):
        try:
            kls.scraping_race_info_in(target_datetime_str)
        except TimeoutException:
            print('Timeout, so retrying... ({TIME}/{MAX})'.format(TIME=i + 1, MAX=parameters['RETRIES']))
            continue
        else:
            print('scraped the web site info in {TARGET_DATE}'.format(TARGET_DATE=target_datetime_str))
            print()
            return True
    print('Failed to scrape the web site info in {TARGET_DATE}'.format(TARGET_DATE=target_datetime_str))
    print()


def scraping_race_info_until_start_date(parameters, kls):
    # scarping nearest future days web info at first time
    target_datetime_list = get_nearest_future_holidays_list()
    for target_datetime_str in reversed(target_datetime_list):
        try_scraping_info_in(parameters, kls, target_datetime_str)

    # after the second time, scraping the past holidays web info
    while True:
        target_datetime = datetime.datetime.strptime(target_datetime_list[0], '%Y%m%d') - datetime.timedelta(days=1)
        target_datetime_list = get_latest_holidays_list(target_datetime)

        for target_datetime_str in reversed(target_datetime_list):
            try_scraping_info_in(parameters, kls, target_datetime_str)

        if parameters['START_DATE'] in target_datetime_list:
            break


if __name__ == '__main__':
    main()
