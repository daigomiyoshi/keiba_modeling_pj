import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import os
import sys
import datetime
import time
import re
import itertools
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, InvalidSessionIdException

def main():
    parameters = {
        'URL_ABOUT_KEIBA_YAHOO': 'https://keiba.yahoo.co.jp/schedule/list/{YEAR}/?place={PLACE}',
        'YEAR_RANGE': range(2020, 2021),
        'PLACE_RANGE': range(1, 11),
        'DRIVER_DIR': 'Config/chromedriver_v83',
        'PAGE_LOAD_TIMEOUT': 10,
    }
    driver = initialize_chrome_driver(parameters)
    race_date_df = get_race_date_df(driver, parameters)
    race_date_df.to_csv('tips/race_calendar_master.csv', index=False)
    

def initialize_chrome_driver(parameters):
    chrome_options = Options()
    chrome_options.add_argument('--dns-prefetch-disable')
    driver = Chrome(executable_path=parameters['DRIVER_DIR'], chrome_options=chrome_options)
    driver.set_page_load_timeout(parameters['PAGE_LOAD_TIMEOUT'])
    driver.maximize_window()
    return driver


def _load_target_url_page(target_url, driver):
    try:
        driver.get(target_url)
        print('We could load the URL:', driver.current_url)
    except (TimeoutException, InvalidSessionIdException) as e:
        print('We could not load the URL because of: ', e)
        driver.refresh()


def _extract_race_date_info(year, place, race_date_and_place_text):
    race_text_1st = re.split('\n', race_date_and_place_text)[0]
    race_text_2nd = re.split('\n', race_date_and_place_text)[1]
    
    race_year = year
    race_month = int(re.split('月|日', race_text_1st)[0])
    race_date = int(re.split('月|日', race_text_1st)[1])
    race_place = place
    race_kai = int(re.split('回|日', race_text_2nd)[0])
    race_nichi = int(re.sub("\\D", "", re.split('回|日', race_text_2nd)[1]))
    
    return [race_year, race_place, race_kai, race_nichi, race_month, race_date]


def _extract_race_date_info(year, place, race_date_and_place_text):
    race_text_1st = re.split('\n', race_date_and_place_text)[0]
    race_text_2nd = re.split('\n', race_date_and_place_text)[1]
    
    race_year = year
    race_month = int(re.split('月|日', race_text_1st)[0])
    race_date = int(re.split('月|日', race_text_1st)[1])
    race_place = place
    race_kai = int(re.split('回|日', race_text_2nd)[0])
    race_nichi = int(re.sub("\\D", "", re.split('回|日', race_text_2nd)[1]))
    
    return [race_year, race_place, race_kai, race_nichi, race_month, race_date]

def _get_round_list(driver, xpath_to_date):
    url_to_round_list = driver.find_element_by_xpath(xpath_to_date+'/a').get_attribute("href")
    _load_target_url_page(url_to_round_list, driver)
    length_of_round = len(driver.find_elements_by_class_name('scheRNo'))
    return list(range(1, length_of_round+1))


def _make_each_year_place_race_date_list(driver, target_url, year, place):
    each_year_place_race_date_list = []
    idx = 2
    while True :
        try:
            _load_target_url_page(target_url, driver)
            xpath_to_date = '//*[@id="wrap"]/div[1]/div[1]/table/tbody/tr[{IDX}]/td[1]'.format(IDX=idx)
            race_date_and_place_text = driver.find_element_by_xpath(xpath_to_date).text
            race_date_info_list = _extract_race_date_info(year, place, race_date_and_place_text)

            round_list = _get_round_list(driver, xpath_to_date)
            each_year_place_race_date_list += [list(itertools.chain.from_iterable([race_date_info_list, [i]])) for i in round_list]

            idx += 2
            time.sleep(1)

        except NoSuchElementException:
            break
    return each_year_place_race_date_list


def get_race_date_df(driver, parameters):
    race_date_df = pd.DataFrame()
    for year in parameters['YEAR_RANGE']:
        for place in parameters['PLACE_RANGE']:
            target_url = parameters['URL_ABOUT_KEIBA_YAHOO'].format(YEAR=year, PLACE=place)
            each_year_place_race_date_list = _make_each_year_place_race_date_list(driver, target_url, year, place)
            race_date_df = pd.concat([race_date_df, pd.DataFrame(each_year_place_race_date_list)])
    
    race_date_df.columns = ['race_year', 'race_place_id', 'race_kai', 'race_nichi', 'race_month', 'race_date', 'race_round']
    race_date_df = race_date_df.loc[:, ['race_year', 'race_place_id', 'race_kai', 'race_nichi', 'race_round', 'race_month', 'race_date']]
    return race_date_df


if __name__ == '__main__':
    main()
