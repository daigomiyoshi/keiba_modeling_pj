import datetime
from selenium import webdriver
from Config import params_config, db_config
from ScrapingTools.KeibaLabScraper import KeibaLabScraper

import warnings
warnings.filterwarnings('ignore')


def main():
    parameters = params_config.parameters
    db_params = db_config.db_params
    driver = initialize_chrome_driver(parameters)
    kls = KeibaLabScraper(driver, parameters, db_params)

    scraping_race_result_until_start_date(parameters, kls)
    scraping_future_race_info(parameters, kls)

    driver.quit()


def initialize_chrome_driver(parameters):
    driver = webdriver.Chrome(executable_path=parameters['DRIVER_DIR'])
    driver.set_page_load_timeout(parameters['PAGE_LOAD_TIMEOUT'])
    driver.maximize_window()
    return driver


def get_today_datetime():
    return datetime.date.today()


def get_latest_holiday_list(target_datetime):
    while True:
        if target_datetime.weekday() == 5:
            saturday_datetime_str = target_datetime.strftime("%Y%m%d")
            target_datetime_plus_1 = target_datetime + datetime.timedelta(days=1)
            sunday_datetime_str = target_datetime_plus_1.strftime("%Y%m%d")
            return [saturday_datetime_str, sunday_datetime_str]
        else:
            target_datetime = target_datetime + datetime.timedelta(days=-1)


def try_scraping_result_info_in(kls, parameters, target_datetime_str):
    for i in range(parameters['RETRIES']):
        try:
            kls.scraping_result_info_in(target_datetime_str)
            print('scraped the web site info in {TARGET_DATE}'.format(TARGET_DATE=target_datetime_str))
        except TimeoutException as e:
            print('Timeout, Retrying... ({I}/{MAX})'.format(I=i, MAX=parameters['RETRIES']))
            continue
        else:
            return True


def scraping_race_result_until_start_date(parameters, kls):
    # scarping web info at first time
    target_datetime = get_today_datetime()
    target_datetime_list = get_latest_holiday_list(target_datetime)
    for target_datetime_str in reversed(target_datetime_list):
        try_scraping_result_info_in(kls, parameters, target_datetime_str)

    # after the second time process for scraping
    while True:
        target_datetime_str = target_datetime_list[0]
        target_datetime = datetime.datetime.strptime(target_datetime_str, '%Y%m%d') - datetime.timedelta(days=1)
        target_datetime_list = get_latest_holiday_list(target_datetime)

        for target_datetime_str in reversed(target_datetime_list):
            # scarping web info in target day
            try_scraping_result_info_in(kls, parameters, target_datetime_str)

        if parameters['START_DATE'] in target_datetime_list:
            break


def scraping_future_race_info(parameters, kls):
    pass


if __name__ == '__main__':
    main()
