import os
import sys
import datetime
import pymysql
import re
import time
import urllib3
from selenium.common.exceptions import NoSuchElementException, TimeoutException, InvalidSessionIdException

this_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(this_dir)
sys.path.append(parent_dir)
from Utils.bulk_insert import BulkInsert


class RaceInfoScraper(object):

    def __init__(self, parameters, db_params, driver):
        self.parameters = parameters
        self.con = pymysql.connect(**db_params)
        self.driver = driver

    # Common functions
    def _fetchall_and_make_list_by(self, query):
        try:
            cursor = self.con.cursor()
            cursor.execute(query)
            fetch_result = cursor.fetchall()
            fetch_result_list = [item for item in fetch_result]
            cursor.close()
            return fetch_result_list
        except Exception as e:
            print(e)

    def _bulk_insert(self, insert_list, target_table_name, insert_col_names):
        try:
            bi = BulkInsert(self.con)
            bi.execute(insert_data=insert_list, target_table=target_table_name, col_names=insert_col_names)
        except RuntimeError as e:
            print(e)
            raise TypeError

    def _load_target_url_page(self, target_url):
        try:
            self.driver.get(target_url)
            print('We could load the URL:', self.driver.current_url)
        except (TimeoutException, InvalidSessionIdException, urllib3.exceptions.MaxRetryError) as e:
            print('We could not load the URL because of: ', e)
            self.driver.refresh()

    # Functions for scraping race master info
    @staticmethod
    def _get_num_str(num):
        num_str = str(num) if num >= 10 else '0' + str(num)
        return num_str

    def _make_race_ids_list(self):
        query = 'SELECT * FROM race_calender_master;'
        return self._fetchall_and_make_list_by(query)

    def _make_race_id_and_target_url(self, race_calender):
        race_id = ''.join(map(lambda x: self._get_num_str(x), race_calender))
        target_url = self.parameters['URL_ABOUT_NETKEIBA']['RACE_TABLE'] + race_id
        return race_id, target_url

    def _is_the_race_id_existing_in_master(self, race_id):
        query_for_master = "SELECT race_id FROM race_master WHERE race_id = '{RACE_ID}'".format(RACE_ID=race_id)
        race_id_list_in_master_existing = self._fetchall_and_make_list_by(query_for_master)
        query_for_table = "SELECT race_id FROM race_table_info WHERE race_id = '{RACE_ID}'".format(RACE_ID=race_id)
        race_id_list_in_table_existing = self._fetchall_and_make_list_by(query_for_table)
        if len(race_id_list_in_master_existing) > 0 and len(race_id_list_in_table_existing) > 0:
            return True
        else:
            return False
    
    def _is_the_race_master_url_having_info(self):
        try:
            self.driver.find_elements_by_xpath('//*[@id="page"]/div[2]/div/div[1]/div[3]/div[2]')[0]  # RaceList_Item02
            int(self.driver.find_element_by_class_name('HorseList').find_elements_by_class_name('Txt_C')[0].text)  # wakuban
            return True
        except (IndexError, ValueError):
            return False

    def _get_race_date(self, race_id):
        race_date_info = driver.find_elements_by_id('RaceList_DateList')[0].find_elements_by_class_name('Active')[0].text
        race_year = race_id[:4]
        try:
            race_month = re.split('月|日|\(|\)', race_date_info)[0]
            race_date = re.split('月|日|\(|\)', race_date_info)[1]
        except IndexError:
            race_month = re.split('/', race_date_info)[0]
            race_date = re.split('/', race_date_info)[1]
        race_date_str = race_year + '-' +race_month + '-' + race_date
        race_dow = datetime.datetime.strptime(race_date_str, '%Y-%m-%d').strftime('%A')[0]
        
        return race_year, race_month, race_date, race_dow

    def _extract_race_master_info(self, race_id):
        xpath_to_race_name = '//*[@id="page"]/div[2]/div/div[1]/div[3]/div[2]'
        race_master_info_elem = self.driver.find_elements_by_xpath(xpath_to_race_name)[0]

        race_title = race_master_info_elem.find_elements_by_class_name('RaceName')[0].text
        race_data_01 = race_master_info_elem.find_elements_by_class_name('RaceData01')[0].text.replace(u'\n',u'')
        starting_time = re.search('(.*)発走', race_data_01.split('/')[0]).group(1)
        race_coure = race_data_01.split('/')[1]
        race_weather = re.search('天候:(.*)', race_data_01.split('/')[2]).group(1)
        race_condition = re.search('馬場:(.*)', race_data_01.split('/')[3]).group(1)
        race_year, race_month, race_date, race_dow = _get_race_date(race_id)        
        race_other_info = re.sub(r"\s+", " ", race_master_info_elem.find_elements_by_class_name('RaceData02')[0].text.replace(u'\n',u' '))

        return ([
            race_id, 
            race_title, 
            race_coure, 
            race_weather, 
            race_condition, 
            race_year, 
            race_month, 
            race_date, 
            race_dow, 
            starting_time, 
            race_other_info
        ])

    @staticmethod
    def _get_horse_weight_and_increment_one(horse_weight_info):
        if horse_weight_info != '':
            horse_weight = int(re.split('\(|\)', horse_weight_info)[0])
            horse_weight_increment = re.split('\(|\)', horse_weight_info)[1]
        else:
            horse_weight = ''
            horse_weight_increment = ''
        return horse_weight, horse_weight_increment

    def _extract_race_table_info(self, race_id):
        table_element_list = self.driver.find_elements_by_class_name('HorseList')
        this_race_table_info = []
        for row in range(len(table_element_list)):
            bracket_num = int(table_element_list[row].find_element_by_xpath('td[1]').text)
            horse_num = int(table_element_list[row].find_element_by_xpath('td[2]').text)
            horse_name = table_element_list[row].find_element_by_xpath('td[4]').text
            href_to_horse = table_element_list[row].find_element_by_xpath('td[4]/div/div/span/a').get_attribute("href")
            horse_age = int(re.sub("\\D", "", table_element_list[row].find_element_by_xpath('td[5]').text))
            horse_sex = re.match('[0-9a-zA-Zあ-んア-ン一-鿐]', table_element_list[row].find_element_by_xpath('td[5]').text).group()

            weight_penalty = table_element_list[row].find_element_by_xpath('td[6]').text
            weight_penalty = float(weight_penalty) if weight_penalty != '' else ''

            jockey_name = table_element_list[row].find_element_by_xpath('td[7]').text
            href_to_jockey = table_element_list[row].find_element_by_xpath('td[7]/a').get_attribute("href")
            owner_name = table_element_list[row].find_element_by_xpath('td[8]/a').text
            href_to_owner = table_element_list[row].find_element_by_xpath('td[8]/a').get_attribute("href")

            try:
                horse_weight_info = table_element_list[row].find_element_by_xpath('td[9]').text
                horse_weight, horse_weight_increment = self._get_horse_weight_and_increment_one(horse_weight_info)
            except ValueError:
                horse_weight, horse_weight_increment = '', ''
                
            win_odds = table_element_list[row].find_element_by_xpath('td[10]').text
            popularity_order = table_element_list[row].find_element_by_xpath('td[11]').text

            this_race_table_info.append([
                race_id,
                bracket_num,
                horse_num,
                horse_name,
                href_to_horse,
                horse_age,
                horse_sex,
                weight_penalty,
                jockey_name,
                href_to_jockey,
                owner_name,
                href_to_owner,
                horse_weight,
                horse_weight_increment,
                win_odds,
                popularity_order
            ])

        return this_race_table_info

    def get_race_master_and_table_info(self):
        race_calender_master_list = self._make_race_ids_list()
        for race_calender in race_calender_master_list:
            race_calender = (2020, 5, 2, 1, 1)
            race_id, target_url = self._make_race_id_and_target_url(race_calender)

            if self._is_the_race_id_existing_in_master(race_id):
                # print('Information about', target_url, 'is already existing in master')
                continue
            
            self._load_target_url_page(target_url)
            if not self._is_the_race_master_url_having_info():
                print('\tThis URL has no information about: ', race_id)
                continue

            race_master_list = self._extract_race_master_info(race_id)
            race_table_info_list = self._extract_race_table_info(race_id)
            self._bulk_insert([race_master_list], 'race_master', self.parameters['TABLE_COL_NAMES']['race_master'])
            self._bulk_insert(race_table_info_list, 'race_table_info', self.parameters['TABLE_COL_NAMES']['race_table_info'])

    # Functions for scraping race result and refund info
    def _extract_race_ids_in_master_not_exist_in_race_result(self):
        query = """
            SELECT DISTINCT race_id 
            FROM race_master
            WHERE 0=0 
            AND race_id NOT IN (SELECT DISTINCT race_id FROM race_result_info)
            AND race_year >= {LATEST_YEAR}
            AND race_month >= {LATEST_MONTH}
        """.format(LATEST_YEAR=self.parameters['LATEST_YEAR'], LATEST_MONTH=self.parameters['LATEST_MONTH'])
        return self. _fetchall_and_make_list_by(query)

    def _make_target_url_about_race_result(self, race_id):
        return self.parameters['URL_ABOUT_NETKEIBA']['RACE_RESULT'].format(RACE_ID=race_id)
    
    def _is_the_race_result_url_having_info(self):
        try:
            self.driver.find_elements_by_class_name('HorseList')
            self.driver.find_element_by_class_name('FullWrap')
            return True
        except IndexError:
            return False

    def _extract_race_result_info(self, race_id):
        this_race_result_info = []
        table_element_list = self.driver.find_elements_by_class_name('HorseList')
        for row in range(len(table_element_list)):
            arrrival_order  = table_element_list[row].find_element_by_xpath('td[1]').text
            bracket_num = table_element_list[row].find_element_by_xpath('td[2]').text
            horse_num = table_element_list[row].find_element_by_xpath('td[3]').text
            arrival_time = table_element_list[row].find_element_by_xpath('td[8]').text
            arrival_diff = table_element_list[row].find_element_by_xpath('td[9]').text
            
            this_race_result_info.append([
                race_id,
                bracket_num,
                horse_num,
                arrival_time,
                arrival_diff,
                arrrival_order
            ])

        return this_race_result_info

    @staticmethod
    def _get_tansho_or_fukusho_result(i, race_id, refund_type, result_list, payout_list, ninki_list):
        return [
            race_id, 
            refund_type,  
            i+1,
            result_list[i],
            payout_list[i],
            ninki_list[i]
    ]

    @staticmethod
    def _get_wide_result(i, race_id, refund_type, result_list, payout_list, ninki_list):
        return [
                race_id, 
                refund_type,  
                int((i+2)/2),
                result_list[i],
                payout_list[int(i/2)],
                ninki_list[int(i/2)]
        ]

    @staticmethod
    def _get_other_result(i, race_id, refund_type, result_list, payout_list, ninki_list):
            return [
                race_id, 
                refund_type,  
                1,
                result_list[i],
                payout_list[0],
                ninki_list[0]
            ]
    
    def _get_payout_info(self, race_id, refund_table_elem, refund_type):
        result_list = re.split('\n | ' '', refund_table_elem.find_elements_by_tag_name('td')[0].text)
        payout_list = re.split('\n | ' '', refund_table_elem.find_elements_by_tag_name('td')[1].text.replace('円', ''))
        ninki_list = re.split('\n | ' '', refund_table_elem.find_elements_by_tag_name('td')[2].text.replace('人気', ''))

        payout_result_list = []
        for i in range(len(result_list)):
            if refund_type in ['単勝', '複勝']:
                payout_result_list.append(self._get_tansho_or_fukusho_result(i, race_id, refund_type, result_list, payout_list, ninki_list))
            elif refund_type in ['ワイド']:
                payout_result_list.append(self._get_wide_result(i, race_id, refund_type, result_list, payout_list, ninki_list))
            else:
                payout_result_list.append(self._get_other_result(i, race_id, refund_type, result_list, payout_list, ninki_list))
            
        return payout_result_list
    
    def _extract_race_refund_info(self, race_id):
        empty_refund_list = []
        refund_table_list = self.driver.find_element_by_class_name('FullWrap').find_elements_by_tag_name('tr')
        for idx in range(len(refund_table_list)):
            refund_table_elem = refund_table_list[idx]
            refund_type = refund_table_elem.find_element_by_tag_name('th').text
            
            empty_refund_list.append(self._get_payout_info(race_id, refund_table_elem, refund_type))

        return empty_refund_list

    def get_race_result_info(self):
        existing_race_ids_in_master = self._extract_race_ids_in_master_not_exist_in_race_result()
        
        for id_idx in range(len(existing_race_ids_in_master)):
            race_id = existing_race_ids_in_master[id_idx][0]
            target_url = self._make_target_url_about_race_result(race_id)
            
            self._load_target_url_page(target_url)
            if not self._is_the_race_result_url_having_info():
                print('\tThis URL has no information about: ', race_id)
                continue

            race_result_info_list = self._extract_race_result_info(race_id)
            race_refund_info_list = self._extract_race_refund_info(race_id)
            self._bulk_insert(race_result_info_list, 'race_result_info', parameters['TABLE_COL_NAMES']['race_result_info'])
            self._bulk_insert(race_refund_info_list, 'race_refund_info', parameters['TABLE_COL_NAMES']['race_refund_info'])                        

    # Functions for scraping race past 5 result
    def _extract_race_ids_in_master_not_exist_in_race_past_5_result(self):
        query = """
            SELECT DISTINCT race_id
            FROM race_master
            WHERE 0=0
            AND race_id NOT IN (SELECT DISTINCT race_id FROM race_past_5_result_info)
            AND race_year >= {LATEST_YEAR}
            AND race_month >= {LATEST_MONTH}
        """.format(LATEST_YEAR=self.parameters['LATEST_YEAR'], LATEST_MONTH=self.parameters['LATEST_MONTH'])
        return self._fetchall_and_make_list_by(query)

    def _make_target_url_about_past_5_race_result(self, race_id):
        return self.parameters['URL_ABOUT_NETKEIBA']['RACE_PAST5_RESULT'].format(RACE_ID=race_id)

    def _extract_past_5_race_result(self, race_id):
        this_race_past5_result_info = []
        table_element = self.driver.find_element_by_class_name('Shutuba_HorseList').find_elements_by_class_name('HorseList')
        table_length = len(table_element)

        for row in range(table_length):
            bracket_num = table_element[row].find_elements_by_tag_name('td')[0].text
            horse_num = table_element[row].find_elements_by_tag_name('td')[1].text

            race_name_elem_list = table_element[row].find_elements_by_class_name('Data_Item')
            for i in range(len(race_name_elem_list)):
                past_x = i+1
                race_name_element = race_name_elem_list[i].find_element_by_class_name('Data02')
                past_x_race_title = race_name_element.text
                past_x_race_id = int(re.sub('\\D', '', race_name_element.find_element_by_tag_name('a').get_attribute("href")))
                arrival_order = race_name_elem_list[i].find_element_by_class_name('Num').text
                this_race_past5_result_info.append([
                    race_id, 
                    bracket_num, 
                    horse_num, 
                    past_x, 
                    past_x_race_title, 
                    past_x_race_id, 
                    arrival_order
                ])

        return this_race_past5_result_info

    def get_past_5_race_result_info(self):
        existing_race_ids_in_master = self._extract_race_ids_in_master_not_exist_in_race_past_5_result()
        
        for id_idx in range(len(existing_race_ids_in_master)):
            race_id = existing_race_ids_in_master[id_idx][0]
            target_url = self._make_target_url_about_past_5_race_result(race_id)
            
            self._load_target_url_page(target_url)

            race_past5_result_info_list = self._extract_past_5_race_result(race_id)
            if len(race_past5_result_info_list) == 0:
                print('\tThis race has no past 5 race result info')
                continue

            self._bulk_insert(race_past5_result_info_list, 'race_past_5_result_info', parameters['TABLE_COL_NAMES']['race_past_5_result_info'])