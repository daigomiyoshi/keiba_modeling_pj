import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Config import params_config
from ScrapingTools import KeibaLabScraper


def main():
    parameters = params_config.parameters
    driver = initialize_chrome_driver(parameters)

    kls = KeibaLabScraper(driver, parameters)

    scraping_race_result_until_start_date(parameters)
    scraping_future_race_info(parameters)

    close_chrome_window(driver)


def initialize_chrome_driver(parameters):
    driver = webdriver.Chrome(executable_path=parameters['DRIVER_DIR'])
    driver.set_page_load_timeout(parameters['PAGE_LOAD_TIMEOUT'])
    driver.maximize_window()
    return driver


def close_chrome_window(driver):
    driver.quit()


def back_chrome_window(driver):
    driver.back()


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


def scraping_race_result_until_start_date(parameters):
    # first process for scraping
    target_datetime = get_today_datetime()  # type: datetime.date
    target_datetime_list = get_latest_holiday_list(target_datetime)

    # scarping keibalab web info
    print('scraping the web site info in {TARGET_DATE}'.format(TARGET_DATE=target_datetime_list[0]))
    print('scraping the web site info in {TARGET_DATE}'.format(TARGET_DATE=target_datetime_list[1]))
    # ENTER MY CODE #

    # after the second time process for scraping
    while True:
        target_datetime_str = target_datetime_list[0]  # type: str
        target_datetime = datetime.datetime.strptime(target_datetime_str, '%Y%m%d') - datetime.timedelta(
            days=1)  # type: datetime.date
        target_datetime_list = get_latest_holiday_list(target_datetime)

        # scarping keibalab web info
        print('scraping the web site info in {TARGET_DATE}'.format(TARGET_DATE=target_datetime_list[0]))
        print('scraping the web site info in {TARGET_DATE}'.format(TARGET_DATE=target_datetime_list[1]))
        # ENTER MY CODE #

        if parameters['START_DATE'] in target_datetime_list:
            break


def scraping_future_race_info(parameters):
    pass


if __name__ == '__main__':
    main()
