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
from selenium.common.exceptions import NoSuchElementException, TimeoutException, InvalidSessionIdException

this_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(this_dir)
sys.path.append(parent_dir)

from Utils.bulk_insert import BulkInsert


class RaceInfoScraper(object):

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
        except (TimeoutException, urllib3.exceptions.MaxRetryError, InvalidSessionIdException) as e:
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

    def _is_race_kakutei(self, xpath_table_of_race_result, table_tbody_idx):
        xpath_for_kakutei_box = \
            xpath_table_of_race_result + '/tbody/tr[{TBODY_IDX}]/td[3]'.format(TBODY_IDX=table_tbody_idx + 1)
        try:
            self.driver.find_element_by_xpath(xpath_for_kakutei_box).find_element_by_tag_name('a')
            return True
        except NoSuchElementException:
            return False

    def _is_race_canceled(self, xpath_tdoby_of_table_race_result):
        try:
            self.driver.find_element_by_xpath(xpath_tdoby_of_table_race_result)
            return False
        except NoSuchElementException:
            return True

    def _make_xpath_list_of_race_result_link(self):
        xpath_list_of_race_result_link = []

        xpath_race_info_div = '//*[@id="raceInfo"]/div[1]'
        race_table_header_list = \
            self.driver.find_element_by_xpath(xpath_race_info_div).find_elements_by_tag_name('table')

        for table_header_idx in range(len(race_table_header_list)):
            xpath_table_of_race_result = \
                xpath_race_info_div + '/table[{TABLE_IDX}]'.format(TABLE_IDX=table_header_idx + 1)
            race_table_body_elem_list = self.driver.find_element_by_xpath(
                xpath_table_of_race_result).find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')

            for table_tbody_idx in range(len(race_table_body_elem_list)):
                xpath_tdoby_of_table_race_result = \
                    xpath_table_of_race_result + '/tbody/tr[{TBODY_IDX}]/td[2]/a'.format(TBODY_IDX=table_tbody_idx + 1)

                if self._is_race_canceled(xpath_tdoby_of_table_race_result):
                    xpath_list_of_race_result_link.append(['canceled', xpath_tdoby_of_table_race_result])
                elif self._is_race_kakutei(xpath_table_of_race_result, table_tbody_idx):
                    xpath_list_of_race_result_link.append(['kakutei', xpath_tdoby_of_table_race_result])
                else:
                    xpath_list_of_race_result_link.append(['not_kakutei', xpath_tdoby_of_table_race_result])

        if xpath_list_of_race_result_link is None:  # case that this day has no races
            return None

        return xpath_list_of_race_result_link

    def _get_race_id(self, xpath_of_race_result_link):
        race_id = \
            int(re.sub('\\D', '', self.driver.current_url.split(self.parameters['TARGET_URL_OF_KAIBALAB_RACE'])[1]))
        while True:
            if len(str(race_id)) != 12:
                print('Failed to get the correct race_id, so retry to get the id')
                self._back_chrome_window_for_number_of(1)
                self._make_web_driver_click_by(xpath_of_race_result_link)
                race_id = int(re.sub('\\D', '', self.driver.current_url.split(
                    self.parameters['TARGET_URL_OF_KAIBALAB_RACE'])[1]))
            else:
                break
        return race_id

    def _is_race_id_existing_in_db(self, race_id):
        select_query = 'SELECT race_id FROM keibalab_race_master WHERE race_id = "{RACE_ID}";'.format(RACE_ID=race_id)
        cursor = self.con.cursor()
        cursor.execute(select_query)
        fetch_result = cursor.fetchone()
        if fetch_result is None:
            return False
        elif int(fetch_result[0]) == race_id:
            return True

    def _get_race_data_box_list(self, race_id):
        race_data_box = self.driver.find_element_by_xpath('//*[@id="tab1"]/div[2]/div[1]/div[1]/div[1]/div[2]')
        race_timing = race_data_box.find_element_by_xpath('//p[@class="bold"]').text
        race_title = race_data_box.find_element_by_xpath('//h1[@class="raceTitle fL"]').text
        try:
            race_weather = race_data_box.find_elements_by_xpath('//div[@class="weather_ground fL"]/ul/li')[0].text
            race_condition = race_data_box.find_elements_by_xpath('//div[@class="weather_ground fL"]/ul/li')[1].text
        except IndexError:
            race_weather = 'unknown'
            race_condition = 'unknown'
        course_syokin_elem = race_data_box.find_elements_by_xpath('//ul[@class="classCourseSyokin clearfix"]/li')
        course_syokin_list = ','.join([course_syokin_elem[i].text.replace('\u3000', ' ')
                                       for i in range(len(course_syokin_elem))]).replace(',', ' ')

        return [race_id, race_timing, race_title, race_weather, race_condition, course_syokin_list]

    def _get_race_result_tbody_list(self, race_id):
        race_result_tbody_row_elem_list = \
            self.driver.find_elements_by_xpath('//*[@class="DbTable stripe resulttable"]/tbody/tr')
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

    def _get_race_prior_info_tbody_list(self, race_id):

        while True:
            xpath_to_web_newspaper = '//*[@id="dbNav"]/div/ul/li[1]/a'
            self._make_web_driver_click_by(xpath_to_web_newspaper, verbose=False)
            xpath_to_yoko_gata = '//*[@id="dbnewWrap"]/div/article/div/section/div[4]/div[1]/div[1]/ul/li[2]/a'
            self._make_web_driver_click_by(xpath_to_yoko_gata, verbose=False)

            race_info_tbody_row_elem_list = self.driver.find_elements_by_xpath('//*[@id="top"]/table/tbody/tr')
            if len(race_info_tbody_row_elem_list) == 0:
                self._back_chrome_window_for_number_of(2)
            else:
                break

        race_info_tbody_list = []
        for i in range(len(race_info_tbody_row_elem_list)):
            post_position = race_info_tbody_row_elem_list[i].find_element_by_xpath('td[1]').text
            horse_number = race_info_tbody_row_elem_list[i].find_element_by_xpath('td[2]').text
            horse_name = race_info_tbody_row_elem_list[i].find_element_by_xpath('td[4]/dl/dd[1]').text
            href_to_the_horse = \
                race_info_tbody_row_elem_list[i].find_element_by_xpath('td[4]/dl/dd[1]/a').get_attribute("href")
            jockey_name = race_info_tbody_row_elem_list[i].find_element_by_xpath('td[4]/dl/dd[2]').text
            href_to_the_jockey = \
                race_info_tbody_row_elem_list[i].find_elements_by_xpath('td[4]/dl/dd[2]/a')[0].get_attribute("href")
            trainer_name = race_info_tbody_row_elem_list[i].find_element_by_xpath('td[4]/dl/dd[3]/a').text
            sex_and_age, interval = \
                race_info_tbody_row_elem_list[i].find_element_by_xpath('td[4]/dl/dd[3]').text.split(trainer_name)
            horse_age = re.sub("\\D", "", sex_and_age)
            horse_sex = re.match('[0-9a-zA-Zあ-んア-ン一-鿐]', sex_and_age).group()

            try:
                popularity_order = race_info_tbody_row_elem_list[i].find_elements_by_xpath('td[5]/dl/dd')[0].text
                win_odds = race_info_tbody_row_elem_list[i].find_elements_by_xpath('td[5]/dl/dd')[1].text
                horse_weight = race_info_tbody_row_elem_list[i].find_elements_by_xpath('td[5]/dl/dd')[2].text
                horse_weight_increment_from_previous = \
                    race_info_tbody_row_elem_list[i].find_elements_by_xpath('td[5]/dl/dd')[3].text

            except IndexError:
                popularity_order = race_info_tbody_row_elem_list[i].find_element_by_xpath('td[5]').text
                win_odds = race_info_tbody_row_elem_list[i].find_element_by_xpath('td[5]').text
                horse_weight = race_info_tbody_row_elem_list[i].find_element_by_xpath('td[5]').text
                horse_weight_increment_from_previous = \
                    race_info_tbody_row_elem_list[i].find_element_by_xpath('td[5]').text

            owner_name = race_info_tbody_row_elem_list[i].find_elements_by_xpath('td[6]/dl/dd/a')[0].text
            href_to_the_owner = \
                race_info_tbody_row_elem_list[i].find_elements_by_xpath('td[6]/dl/dd/a')[0].get_attribute("href")
            breeder_name = race_info_tbody_row_elem_list[i].find_elements_by_xpath('td[6]/dl/dd/a')[1].text

            jockey_finish_first_second = race_info_tbody_row_elem_list[i].find_elements_by_xpath('td[7]/i')[0].text
            horse_number_finish_first_second = \
                race_info_tbody_row_elem_list[i].find_elements_by_xpath('td[7]/i')[1].text
            stallion_finish_first_second = race_info_tbody_row_elem_list[i].find_elements_by_xpath('td[7]/i')[2].text
            conbi_finish_first_second = race_info_tbody_row_elem_list[i].find_elements_by_xpath('td[7]/i')[3].text

            zensou_info_elem = race_info_tbody_row_elem_list[i].find_elements_by_xpath('td/a/dl')
            zensou_info_list = [(zensou_info_elem[i].text.replace('\n', ' ').replace('  ', ' '))
                                for i in range(len(zensou_info_elem))]
            zensou_info_list = [[zensou_info_list[i].replace(' ', ',')] for i in range(len(zensou_info_elem))]
            zensou_info_list = str(zensou_info_list).replace('\'', '')

            race_info_tbody_list.append(
                [race_id, post_position, horse_number, horse_name, href_to_the_horse, jockey_name, href_to_the_jockey,
                 trainer_name, horse_age, horse_sex, popularity_order, win_odds, horse_weight,
                 horse_weight_increment_from_previous, owner_name, href_to_the_owner, breeder_name,
                 jockey_finish_first_second, horse_number_finish_first_second, stallion_finish_first_second,
                 conbi_finish_first_second, zensou_info_list])

        return race_info_tbody_list

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

    def scraping_race_info_in(self, target_datetime_str):
        num_of_index_when_failed = 0
        for i in range(self.parameters['RETRIES']):
            try:
                self._load_target_url_page(target_datetime_str)
                xpath_list_of_race_result_link = self._make_xpath_list_of_race_result_link()
                if xpath_list_of_race_result_link is None:
                    print('This this day has no races')
                    return None

                for j in range(len(xpath_list_of_race_result_link)):
                    num_of_index = copy.deepcopy(j)
                    if j < num_of_index_when_failed:
                        continue

                    xpath_of_race_result_link = xpath_list_of_race_result_link[j]
                    if xpath_of_race_result_link[0] == 'canceled':
                        print('This race is canceled')
                        continue

                    self._make_web_driver_click_by(xpath_of_race_result_link[1])
                    race_id = self._get_race_id(xpath_of_race_result_link[1])
                    if self._is_race_id_existing_in_db(race_id):
                        print('This race id is existing in database, thus go to next race id')
                        self._back_chrome_window_for_number_of(1)
                        time.sleep(1)
                        continue

                    if xpath_of_race_result_link[0] == 'kakutei':
                        race_data_box_list = self._get_race_data_box_list(race_id)
                        race_result_tbody_list = self._get_race_result_tbody_list(race_id)
                        race_prior_info_tbody_list = self._get_race_prior_info_tbody_list(race_id)

                        self._bulk_insert(race_id,
                                          race_result_tbody_list,
                                          'keibalab_race_result_list',
                                          self.parameters['TABLE_COL_NAMES']['keibalab_race_result_list'])
                        self._bulk_insert(race_id,
                                          race_prior_info_tbody_list,
                                          'keibalab_race_prior_info_list',
                                          self.parameters['TABLE_COL_NAMES']['keibalab_race_prior_info_list'])
                        self._bulk_insert(race_id,
                                          [race_data_box_list],
                                          'keibalab_race_master',
                                          self.parameters['TABLE_COL_NAMES']['keibalab_race_master'])
                        self._back_chrome_window_for_number_of(3)
                        time.sleep(1)

                    elif xpath_of_race_result_link[0] == 'not_kakutei':
                        race_data_box_list = self._get_race_data_box_list(race_id)
                        race_prior_info_tbody_list = self._get_race_prior_info_tbody_list(race_id)

                        if race_prior_info_tbody_list is None:
                            print('This day has no prior information, thus go to the next day')
                            break

                        self._bulk_insert(race_id,
                                          race_prior_info_tbody_list,
                                          'keibalab_race_prior_info_list',
                                          self.parameters['TABLE_COL_NAMES']['keibalab_race_prior_info_list'])
                        self._bulk_insert(race_id,
                                          [race_data_box_list],
                                          'keibalab_race_master',
                                          self.parameters['TABLE_COL_NAMES']['keibalab_race_master'])
                        self._back_chrome_window_for_number_of(2)
                        time.sleep(1)

            except (NoSuchElementException, TimeoutException, IndexError, TypeError):
                print('Timeout or Error, so retrying... ({TIME}/{MAX})'.
                      format(TIME=i + 1, MAX=self.parameters['RETRIES']))
                num_of_index_when_failed = num_of_index
                continue
            else:
                return None
        raise TimeoutException
