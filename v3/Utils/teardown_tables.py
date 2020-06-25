import pymysql
import os
import sys

this_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(this_dir)
sys.path.append(parent_dir)

from Config.db_config import db_params


def prepare_queries(table_list):
    truncate_query_list = []
    for each_table in table_list:
        truncate_query_list.append(
            'TRUNCATE TABLE {};'.format(each_table)
        )
    return truncate_query_list


def execute_query(query, db_params):
    try:
        connection = pymysql.connect(**db_params)
        cursor = connection.cursor()
        cursor.execute(query)
        cursor.close()
        connection.commit()
    except Exception as e:
        print(e)


def teardown(table_list):
    queries = prepare_queries(table_list)

    for query in queries:
        print(query)
        execute_query(query, db_params)
