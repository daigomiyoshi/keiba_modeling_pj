import os
import sys
import re
import time
import copy
import urllib3
import pymysql
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

this_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(this_dir)
sys.path.append(parent_dir)

from Utils.bulk_insert import BulkInsert


class HorseInfoScraper(object):

    def __init__(self, driver, parameters, db_params):
        self.driver = driver
        self.parameters = parameters
        self.con = pymysql.connect(**db_params)

    def _back_chrome_window_for_number_of(self, times):
        for _ in range(times):
            self.driver.back()
        return None

    def _load_target_url_page(self, target_datetime_str):
        target_url = self.parameters['TARGET_URL_OF_KAIBALAB_RACE'] + target_datetime_str
        try:
            self.driver.get(target_url)
            print('We could load the URL:', self.driver.current_url)
        except (TimeoutException, urllib3.exceptions.MaxRetryError) as e:
            print(e)
            self.driver.refresh()

    def _make_web_driver_click_by(self, xpath, verbose=True):
        for i in range(self.parameters['RETRIES_WHEN_WEB_CLICK']):
            try:
                WebDriverWait(self.driver, self.parameters['PAGE_LOAD_TIMEOUT']).until(
                    EC.element_to_be_clickable((By.XPATH, xpath)))
                self.driver.find_element_by_xpath(xpath).click()
            except TimeoutException:
                print('Timeout when web_driver_click, so retrying... ({TIME}/{MAX})'.
                      format(TIME=i+1, MAX=self.parameters['RETRIES_WHEN_WEB_CLICK']))
                continue
            else:
                if verbose:
                    print('We could load the XPATH and now locate in:', self.driver.current_url)
                return None
        raise NoSuchElementException

    def _execute_query(self, query):
        try:
            cursor = self.con.cursor()
            cursor.execute(query)
            cursor.close()
            self.con.commit()
        except Exception as e:
            print(e)

    def _truncate_target_rows(self, race_id):
        queries = [
            'TRUNCATE TABLE keibalab_race_master WHERE race_id = "{RACE_ID}";'.format(RACE_ID=race_id),
            'TRUNCATE TABLE keibalab_race_result_list WHERE race_id = "{RACE_ID}";'.format(RACE_ID=race_id),
            'TRUNCATE TABLE keibalab_race_prior_info_list WHERE race_id = "{RACE_ID}";'.format(RACE_ID=race_id)
        ]
        for query in queries:
            print(query)
            self._execute_query(query)

    def _bulk_insert(self, race_id, insert_list, target_table_name, insert_col_names):
        try:
            bi = BulkInsert(self.con)
            bi.execute(insert_data=insert_list, target_table=target_table_name, col_names=insert_col_names)
        except TypeError as e:
            print(e)
            self._truncate_target_rows(race_id)
            raise TypeError

    def scraping_horse_info(self, target_datetime_str):
        pass
