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

    def _make_target_url_about_race_result(self, race_id):
        return self.parameters['URL_ABOUT_NETKEIBA']['RACE_RESULT'].format(RACE_ID=race_id)

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

    def _is_the_race_id_existing_in_master(self, race_id):
        query = """
            SELECT race_id 
            FROM race_master
            WHERE race_id = "RACE_ID;
        """.format(RACE_ID=race_id)
        race_id_list_in_master = self._fetchall_and_make_list_by(query)
        if len(race_id_list_in_master) > 0:
            return True
        else:
            return False

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
            'DELETE FROM race_master WHERE race_id = "{RACE_ID}";'.format(RACE_ID=race_id),
            'DELETE FROM race_table_info WHERE race_id = "{RACE_ID}";'.format(RACE_ID=race_id),
            'DELETE FROM race_result_info WHERE race_id = "{RACE_ID}";'.format(RACE_ID=race_id),
            'DELETE FROM race_refund_info WHERE race_id = "{RACE_ID}";'.format(RACE_ID=race_id)
        ]
        for query in queries:
            print(query)
            self._execute_query(query)

    def _bulk_insert(self, race_id, insert_list, target_table_name, insert_col_names):
        try:
            bi = BulkInsert(self.con)
            bi.execute(insert_data=insert_list, target_table=target_table_name, col_names=insert_col_names)
        except RuntimeError as e:
            print(e)
            self._truncate_target_rows(race_id)
            raise TypeError

    def get_race_master_and_table_info(self):
        for event_year in range(2008, 2020):
            for event_place in range(1, 11):
                for event_month in range(1, 11):
                    for event_time in range(1, 11):
                        for event_race in range(1, 13):
                            race_master_list = []
                            race_table_info_list = []

                            race_id, target_url = self._make_race_id_and_target_url(
                                event_year, event_place, event_month, event_time, event_race
                            )

                            if self._is_the_race_id_existing_in_master(race_id):
                                print('Info about', target_url, 'is already existing in master.')
                                break

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

    def _extract_race_ids_in_master(self):
        query = """
            SELECT DISTINCT race_id 
            FROM race_master
            WHERE race_id NOT IN (SELECT DISTINCT race_id FROM race_result_info);
        """
        return self. _fetchall_and_make_list_by(query)

    @staticmethod
    def _extract_race_result_info(soup, race_id):
        this_race_result_info = []
        table_length = len(soup.find('table', class_='race_table_01 nk_tb_common').find_all('tr'))

        for row in range(1, table_length):
            arrival_order = soup.find('table', class_='race_table_01 nk_tb_common').find_all('tr')[row].find_all('td')[0].text
            bracket_num = soup.find('table', class_='race_table_01 nk_tb_common').find_all('tr')[row].find_all('td')[1].text
            horse_num = soup.find('table', class_='race_table_01 nk_tb_common').find_all('tr')[row].find_all('td')[2].text
            arrival_time = soup.find('table', class_='race_table_01 nk_tb_common').find_all('tr')[row].find_all('td')[7].text
            arrival_diff = soup.find('table', class_='race_table_01 nk_tb_common').find_all('tr')[row].find_all('td')[8].text

            this_race_result_info.append([
                race_id,
                bracket_num,
                horse_num,
                arrival_time,
                arrival_diff,
                arrival_order
            ])

        return this_race_result_info

    @staticmethod
    def _extract_race_refund_info(soup, race_id):
        empty_refund_list = []
        refund_table_list = soup.find('dd', class_='fc').find_all('tr')
        for i in range(len(refund_table_list)):
            refund_table = refund_table_list[i]
            refund_type = refund_table.find('th').text

            if refund_type == '単勝':
                empty_refund_list.append(
                    [race_id, '単勝', 1,
                     int(refund_table.find_all('td')[0].text),
                     int(refund_table.find_all('td')[1].text.split('円')[0].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[0].replace(',', ''))]
                )

            elif refund_type == '複勝':
                empty_refund_list.append(
                    [race_id, '複勝', 1,
                     int(refund_table.find_all('td')[0].text[:2]),
                     int(refund_table.find_all('td')[1].text.split('円')[0].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[0].replace(',', ''))]
                )
                empty_refund_list.append(
                    [race_id, '複勝', 2,
                     int(refund_table.find_all('td')[0].text[2:4]),
                     int(refund_table.find_all('td')[1].text.split('円')[1].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[1].replace(',', ''))]
                )
                try:
                    empty_refund_list.append(
                        [race_id, '複勝', 3,
                         int(refund_table.find_all('td')[0].text[4:6]),
                         int(refund_table.find_all('td')[1].text.split('円')[2].replace(',', '')),
                         int(refund_table.find_all('td')[2].text.split('人気')[2].replace(',', ''))]
                    )
                except ValueError:
                    pass

            elif refund_type == '枠連':
                empty_refund_list.append(
                    [race_id, '枠連', 1,
                     int(refund_table.find_all('td')[0].text.split('-')[0]),
                     int(refund_table.find_all('td')[1].text.split('円')[0].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[0].replace(',', ''))],
                )
                empty_refund_list.append(
                    [race_id, '枠連', 1,
                     int(refund_table.find_all('td')[0].text.split('-')[1]),
                     int(refund_table.find_all('td')[1].text.split('円')[0].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[0].replace(',', ''))]
                )

            elif refund_type == '馬連':
                empty_refund_list.append(
                    [race_id, '馬連', 1,
                     int(refund_table.find_all('td')[0].text.split('-')[0]),
                     int(refund_table.find_all('td')[1].text.split('円')[0].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[0].replace(',', ''))],
                )
                empty_refund_list.append(
                    [race_id, '馬連', 1,
                     int(refund_table.find_all('td')[0].text.split('-')[1]),
                     int(refund_table.find_all('td')[1].text.split('円')[0].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[0].replace(',', ''))]
                )

            elif refund_type == 'ワイド':
                empty_refund_list.append(
                    [race_id, 'ワイド', 1,
                     int(refund_table.find_all('td')[0].text[:2]),
                     int(refund_table.find_all('td')[1].text.split('円')[0].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[0].replace(',', ''))]
                )
                empty_refund_list.append(
                    [race_id, 'ワイド', 1,
                     int(refund_table.find_all('td')[0].text[5:7]),
                     int(refund_table.find_all('td')[1].text.split('円')[0].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[0].replace(',', ''))]
                )
                empty_refund_list.append(
                    [race_id, 'ワイド', 2,
                     int(refund_table.find_all('td')[0].text[7:9]),
                     int(refund_table.find_all('td')[1].text.split('円')[1].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[1].replace(',', ''))]
                )
                empty_refund_list.append(
                    [race_id, 'ワイド', 2,
                     int(refund_table.find_all('td')[0].text[12:14]),
                     int(refund_table.find_all('td')[1].text.split('円')[1].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[1])],
                )
                empty_refund_list.append(
                    [race_id, 'ワイド', 3,
                     int(refund_table.find_all('td')[0].text[14:16]),
                     int(refund_table.find_all('td')[1].text.split('円')[2].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[2].replace(',', ''))]
                )
                empty_refund_list.append(
                    [race_id, 'ワイド', 3,
                     int(refund_table.find_all('td')[0].text[19:22]),
                     int(refund_table.find_all('td')[1].text.split('円')[2].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[2].replace(',', ''))]
                )

            elif refund_type == '馬単':
                empty_refund_list.append(
                    [race_id, '馬単', 1,
                     int(refund_table.find_all('td')[0].text.split('→')[0]),
                     int(refund_table.find_all('td')[1].text.split('円')[0].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[0].replace(',', ''))]
                )
                empty_refund_list.append(
                    [race_id, '馬単', 1,
                     int(refund_table.find_all('td')[0].text.split('→')[1]),
                     int(refund_table.find_all('td')[1].text.split('円')[0].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[0])]
                )

            elif refund_type == '三連複':
                empty_refund_list.append(
                    [race_id, '三連複', 1,
                     int(refund_table.find_all('td')[0].text.split('-')[0]),
                     int(refund_table.find_all('td')[1].text.split('円')[0].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[0].replace(',', ''))]
                )
                empty_refund_list.append(
                    [race_id, '三連複', 1,
                     int(refund_table.find_all('td')[0].text.split('-')[1]),
                     int(refund_table.find_all('td')[1].text.split('円')[0].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[0].replace(',', ''))]
                )
                empty_refund_list.append(
                    [race_id, '三連複', 1,
                     int(refund_table.find_all('td')[0].text.split('-')[2]),
                     int(refund_table.find_all('td')[1].text.split('円')[0].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[0].replace(',', ''))]
                )

            elif refund_type == '三連単':
                empty_refund_list.append(
                    [race_id, '三連単', 1,
                     int(refund_table.find_all('td')[0].text.split('→')[0]),
                     int(refund_table.find_all('td')[1].text.split('円')[0].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[0].replace(',', ''))]
                )
                empty_refund_list.append(
                    [race_id, '三連単', 1,
                     int(refund_table.find_all('td')[0].text.split('→')[1]),
                     int(refund_table.find_all('td')[1].text.split('円')[0].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[0].replace(',', ''))]
                )
                empty_refund_list.append(
                    [race_id, '三連単', 1,
                     int(refund_table.find_all('td')[0].text.split('→')[2]),
                     int(refund_table.find_all('td')[1].text.split('円')[0].replace(',', '')),
                     int(refund_table.find_all('td')[2].text.split('人気')[0].replace(',', ''))]
                )

        return empty_refund_list

    def get_race_result_info(self):
        existing_race_ids_in_master = self._extract_race_ids_in_master()

        for id_idx in range(len(existing_race_ids_in_master)):
            race_id = existing_race_ids_in_master[id_idx][0]
            target_url = self._make_target_url_about_race_result(race_id)

            html = requests.get(target_url)
            html.encoding = 'EUC-JP'
            soup = BeautifulSoup(html.text, 'html.parser')

            if not soup.find_all('table', attrs={'class', 'race_table_01 nk_tb_common'}):
                print('Target URL to requests ', target_url, 'does not exist.')
                break

            print('Target URL to requests: ', target_url)
            race_result_info_list = self._extract_race_result_info(soup, race_id)
            race_refund_info_list = self._extract_race_refund_info(soup, race_id)

            self._bulk_insert(race_id, race_result_info_list, 'race_result_info',
                              self.parameters['TABLE_COL_NAMES']['race_result_info'])
            self._bulk_insert(race_id, race_refund_info_list, 'race_refund_info',
                              self.parameters['TABLE_COL_NAMES']['race_refund_info'])

            time.sleep(1)
