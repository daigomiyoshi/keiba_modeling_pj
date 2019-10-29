import os
import sys
from bs4 import BeautifulSoup
import pymysql
import requests
import re
import time

this_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(this_dir)
sys.path.append(parent_dir)

from Utils.bulk_insert import BulkInsert


class RaceInfoScraper(object):

    def __init__(self, parameters, db_params):
        self.parameters = parameters
        self.con = pymysql.connect(**db_params)

    @staticmethod
    def _get_num_str(num):
        num_str = str(num) if num >= 10 else '0' + str(num)
        return num_str

    def _make_race_id_and_target_url(self, event_year, event_place, event_month, event_time, event_race):
        race_id = str(event_year) + self._get_num_str(event_place) + self._get_num_str(event_month) + self._get_num_str(
            event_time) + self._get_num_str(event_race)
        target_url = self.parameters['URL_ABOUT_NETKEIBA']['RACE_TABLE'] + race_id

        return race_id, target_url

    @staticmethod
    def _extract_common_info(soup, race_id):
        race_title = soup.find('div', class_='data_intro').find('h1').text.replace(u'\xa0', u' ')

        race_course = soup.find('div', class_='data_intro').find_all('p')[0].text.replace(u'\xa0', u' ')

        race_weather = soup.find('div', class_='data_intro').find_all('p')[1].text.replace(u'\xa0', u' ').split('/')[0]
        race_weather = re.search('天気：(.*)', race_weather).group(1)

        race_condition = soup.find('div', class_='data_intro').find_all('p')[1].text.replace(u'\xa0', u' ').split('/')[1]
        race_condition = re.search('馬場：(.*)', race_condition).group(1)

        starting_time = soup.find('div', class_='data_intro').find_all('p')[1].text.replace(u'\xa0', u' ').split('/')[2]
        starting_time = re.search('発走：(.*)', starting_time).group(1)

        race_date_info = soup.find('div', class_='data_intro').find('div', class_='race_otherdata').find_all('p')[0].text
        race_year = re.split('/|\(|\)', race_date_info)[0]
        race_month = re.split('/|\(|\)', race_date_info)[1]
        race_date = re.split('/|\(|\)', race_date_info)[2]
        race_dow = re.split('/|\(|\)', race_date_info)[3]

        race_info_1 = soup.find('div', class_='data_intro').find('div', class_='race_otherdata').find_all('p')[1].text.replace(u'\xa0', u' ')
        race_info_2 = soup.find('div', class_='data_intro').find('div', class_='race_otherdata').find_all('p')[2].text.replace(u'\xa0', u' ')
        race_info_3 = soup.find('div', class_='data_intro').find('div', class_='race_otherdata').find_all('p')[3].text.replace(u'\xa0', u' ')

        return race_id, race_title, race_course, race_weather, race_condition, race_year, race_month, race_date, race_dow, starting_time, race_info_1, race_info_2, race_info_3

    @staticmethod
    def _extract_race_table(soup, race_id):
        this_race_table_info = []
        table_length = len(soup.find('table', class_='race_table_old nk_tb_common').find_all('tr'))
        for row in range(3, table_length):
            bracket_num = int(soup.find('table', class_='race_table_old nk_tb_common').find_all('tr')[row].find_all('td')[0].text)
            horse_num = int(soup.find('table', class_='race_table_old nk_tb_common').find_all('tr')[row].find_all('td')[1].text)
            horse_name = soup.find('table', class_='race_table_old nk_tb_common').find_all('tr')[row].find_all('td')[3].find('a').text
            sex_and_age = soup.find('table', class_='race_table_old nk_tb_common').find_all('tr')[row].find_all('td')[4].text
            horse_sex = int(re.sub("\\D", "", sex_and_age))
            horse_age = re.match('[0-9a-zA-Zあ-んア-ン一-鿐]', sex_and_age).group()
            weight_penalty = float(soup.find('table', class_='race_table_old nk_tb_common').find_all('tr')[row].find_all('td')[5].text)
            jockey_name = soup.find('table', class_='race_table_old nk_tb_common').find_all('tr')[row].find_all('td')[6].text
            href_to_jockey = soup.find('table', class_='race_table_old nk_tb_common').find_all('tr')[row].find_all('td')[6].find('a').attrs['href']
            owner_name = soup.find('table', class_='race_table_old nk_tb_common').find_all('tr')[row].find_all('td')[7].text
            href_to_owner = soup.find('table', class_='race_table_old nk_tb_common').find_all('tr')[row].find_all('td')[7].find('a').attrs['href']

            horse_weight_info = soup.find('table', class_='race_table_old nk_tb_common').find_all('tr')[3].find_all('td')[8].text
            if horse_weight_info != '':
                horse_weight = int(re.split('\(|\)', horse_weight_info)[0])
                horse_weight_increment = re.split('\(|\)', horse_weight_info)[1]
            else:
                horse_weight = ''
                horse_weight_increment = ''

            win_odds = soup.find('table', class_='race_table_old nk_tb_common').find_all('tr')[row].find_all('td')[9].text
            popularity_order = soup.find('table', class_='race_table_old nk_tb_common').find_all('tr')[row].find_all('td')[10].text

            this_race_table_info.append([
                race_id,
                bracket_num,
                horse_num,
                horse_name,
                horse_sex,
                horse_age,
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
            'TRUNCATE TABLE race_master WHERE race_id = "{RACE_ID}";'.format(RACE_ID=race_id),
            'TRUNCATE TABLE race_table_info WHERE race_id = "{RACE_ID}";'.format(RACE_ID=race_id)
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

    def get_race_master_and_table_info(self):
        for event_year in range(2019, 2020):
            for event_place in range(1, 11):
                for event_month in range(1, 11):
                    for event_time in range(1, 11):
                        for event_race in range(1, 13):
                            race_master_list = []
                            race_table_info_list = []

                            race_id, target_url = \
                                self._make_race_id_and_target_url(
                                    event_year, event_place, event_month, event_time, event_race
                                )
                            html = requests.get(target_url)
                            html.encoding = 'EUC-JP'
                            soup = BeautifulSoup(html.text, 'html.parser')

                            if not soup.find_all('table', attrs={'class', 'race_table_old nk_tb_common'}):
                                print('Target URL to requests ', target_url, 'does not exist.')
                                break

                            print('Target URL to requests: ', target_url)
                            race_master_list.append(self._extract_common_info(soup, race_id))
                            race_table_info_list = race_table_info_list + self._extract_race_table(soup, race_id)
                            self._bulk_insert(race_id, race_master_list, 'race_master',
                                              self.parameters['TABLE_COL_NAMES']['race_master'])
                            self._bulk_insert(race_id, race_table_info_list, 'race_table_info',
                                              self.parameters['TABLE_COL_NAMES']['race_table_info'])

                            time.sleep(1)
