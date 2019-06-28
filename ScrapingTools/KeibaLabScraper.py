import os
import sys
import time
import re
import pymysql
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

this_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(this_dir)
sys.path.append(parent_dir)

from Utils.bulk_insert import BulkInsert


class KeibaLabScraper(object):

    def __init__(self, driver, parameters, db_params):
        self.driver = driver
        self.parameters = parameters
        # self.con = pymysql.connect(**db_params)

    def load_target_url_page(self, target_datetime_str):
        target_url = self.parameters['TARGET_URL'] + target_datetime_str

        try:
            self.driver.get(target_url)
            print('We can load the URL:', self.driver.current_url)
        except Exception as e:
            print(e)

    def make_web_driver_click_by(self, xpath, verbose=True):
        try:
            WebDriverWait(self.driver, self.parameters['PAGE_LOAD_TIMEOUT']).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            self.driver.find_element_by_xpath(xpath).click()

            if verbose:
                print('We can load the XPATH and now locate in:', self.driver.current_url)

        except Exception as e:
            print(e)

    def make_xpath_list_of_race_result_link(self):
        xpath_list_of_race_result_link = []

        xpath_race_info_div = '//*[@id="raceInfo"]/div[1]'
        race_table_header_list = self.driver.find_element_by_xpath(
            xpath_race_info_div).find_elements_by_tag_name('table')

        for table_header_idx in range(len(race_table_header_list)):
            xpath_table_of_race_result = \
                xpath_race_info_div + '/table[{TABLE_IDX}]'.format(TABLE_IDX=table_header_idx + 1)
            race_table_body_elem_list = self.driver.find_element_by_xpath(
                xpath_table_of_race_result).find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')

            for table_tbody_idx in range(len(race_table_body_elem_list)):
                xpath_tdoby_of_table_race_result = \
                    xpath_table_of_race_result + '/tbody/tr[{TBODY_IDX}]/td[2]/a'.format(TBODY_IDX=table_tbody_idx + 1)
                xpath_list_of_race_result_link.append(xpath_tdoby_of_table_race_result)

        return xpath_list_of_race_result_link

    def get_race_id(self):
        return int(re.sub('\\D', '', self.driver.current_url.split(self.parameters['TARGET_URL'])[1]))

    def scraping_result_info_in(self, target_datetime_str):
        self.load_target_url_page(target_datetime_str)
        xpath_list_of_race_result_link = self.make_xpath_list_of_race_result_link()
        for xpath_of_race_result_link in xpath_list_of_race_result_link:
            self.make_web_driver_click_by(xpath_of_race_result_link)
            race_id = self.get_race_id()

            self.driver.back()
            time.sleep(1)

    def bulk_insert(self, insert_list, target_table_name, insert_col_names):
        bi = BulkInsert(self.con)
        bi.execute(insert_data=insert_list, target_table=target_table_name, col_names=insert_col_names)
