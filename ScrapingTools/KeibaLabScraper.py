import os
import sys
import re
import pymysql
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
        self.con = pymysql.connect(**db_params)

    def _load_target_url_page(self, target_datetime_str):
        target_url = self.parameters['TARGET_URL'] + target_datetime_str

        try:
            self.driver.get(target_url)
            print('We can load the URL:', self.driver.current_url)
        except Exception as e:
            print(e)

    def _make_web_driver_click_by(self, xpath, verbose=True):
        try:
            WebDriverWait(self.driver, self.parameters['PAGE_LOAD_TIMEOUT']).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            self.driver.find_element_by_xpath(xpath).click()

            if verbose:
                print('We can load the XPATH and now locate in:', self.driver.current_url)

        except Exception as e:
            print(e)

    def _make_xpath_list_of_race_result_link(self):
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

    def _get_race_id(self):
        return int(re.sub('\\D', '', self.driver.current_url.split(self.parameters['TARGET_URL'])[1]))

    def _get_race_data_box_list(self, race_id):
        race_data_box = self.driver.find_element_by_xpath('//*[@id="tab1"]/div[2]/div[1]/div[1]/div[1]/div[2]')
        race_timing = race_data_box.find_element_by_xpath('//p[@class="bold"]').text
        race_title = race_data_box.find_element_by_xpath('//h1[@class="raceTitle fL"]').text
        race_weather = race_data_box.find_elements_by_xpath('//div[@class="weather_ground fL"]/ul/li')[0].text
        race_condition = race_data_box.find_elements_by_xpath('//div[@class="weather_ground fL"]/ul/li')[1].text
        course_syokin_elem = race_data_box.find_elements_by_xpath('//ul[@class="classCourseSyokin clearfix"]/li')
        course_syokin_list = ','.join([course_syokin_elem[i].text.replace('\u3000', ' ')
                                       for i in range(len(course_syokin_elem))]).replace(',', ' ')

        return [race_id, race_timing, race_title, race_weather, race_condition, course_syokin_list]

    def _get_race_result_tbody_list(self, race_id):
        race_result_tbody_row_elem_list = self.driver.find_elements_by_xpath(
            '//*[@class="DbTable stripe resulttable"]/tbody/tr')
        race_result_tbody_list = []

        for i in range(len(race_result_tbody_row_elem_list)):
            arrival_order = race_result_tbody_row_elem_list[i].find_element_by_xpath('td[1]').text
            post_position = race_result_tbody_row_elem_list[i].find_element_by_xpath('td[2]').text

            horse_number = race_result_tbody_row_elem_list[i].find_element_by_xpath('td[3]').text
            horse_name = race_result_tbody_row_elem_list[i].find_element_by_xpath('td[4]').text
            href_to_the_horse = race_result_tbody_row_elem_list[i].find_element_by_xpath('td[4]/a').\
                get_attribute("href")
            horse_age = race_result_tbody_row_elem_list[i].find_element_by_xpath('td[5]').text
            horse_weight = race_result_tbody_row_elem_list[i].find_element_by_xpath('td[15]').text
            horse_impost = race_result_tbody_row_elem_list[i].find_element_by_xpath('td[6]').text

            jockey_name = race_result_tbody_row_elem_list[i].find_element_by_xpath('td[7]').text
            href_to_the_jockey = race_result_tbody_row_elem_list[i].find_element_by_xpath('td[7]/a').\
                get_attribute("href")

            popularity_order = race_result_tbody_row_elem_list[i].find_element_by_xpath('td[8]').text
            win_odds = race_result_tbody_row_elem_list[i].find_element_by_xpath('td[9]').text

            trainer_name = race_result_tbody_row_elem_list[i].find_element_by_xpath('td[14]').text
            href_to_the_trainer = race_result_tbody_row_elem_list[i].find_element_by_xpath('td[14]/a').\
                get_attribute("href")

            race_result_tbody_list.append(
                [race_id, arrival_order, post_position, horse_number, horse_name, href_to_the_horse, horse_age,
                 horse_weight, horse_impost, jockey_name, href_to_the_jockey, popularity_order, win_odds, trainer_name,
                 href_to_the_trainer])

        return race_result_tbody_list

    def _bulk_insert(self, insert_list, target_table_name, insert_col_names):
        bi = BulkInsert(self.con)
        bi.execute(insert_data=insert_list, target_table=target_table_name, col_names=insert_col_names)

    def scraping_result_info_in(self, target_datetime_str):
        self._load_target_url_page(target_datetime_str)
        xpath_list_of_race_result_link = self._make_xpath_list_of_race_result_link()
        # race_data_box = []
        # race_result_table = []
        for xpath_of_race_result_link in xpath_list_of_race_result_link:
            self._make_web_driver_click_by(xpath_of_race_result_link)
            race_id = self._get_race_id()
            race_data_box_list = self._get_race_data_box_list(race_id)
            race_result_tbody_list = self._get_race_result_tbody_list(race_id)

            self._bulk_insert(insert_list=[race_data_box_list],
                              target_table_name='keibalab_race_master',
                              insert_col_names=self.parameters['TABLE_COL_NAMES']['keibalab_race_master'])
            self._bulk_insert(insert_list=race_result_tbody_list,
                              target_table_name='keibalab_race_result_list',
                              insert_col_names=self.parameters['TABLE_COL_NAMES']['keibalab_race_result_list'])

            # race_data_box.append(race_data_box_list)
            # race_result_table.append(race_result_tbody_list)

            self.driver.back()
