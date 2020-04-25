import pymysql
import os
import sys

this_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(this_dir)
sys.path.append(parent_dir)

from Config.db_config import db_params


def prepare_queries():
    return [
        # 'TRUNCATE TABLE race_master;',
        # 'TRUNCATE TABLE race_table_info;',
        # 'TRUNCATE TABLE race_result_info;',
        # 'TRUNCATE TABLE race_refund_info;'
        'TRUNCATE TABLE race_predicted_score;'
    ]


def teardown():
    queries = prepare_queries()

    for query in queries:
        print(query)
        execute_query(query, db_params)


def execute_query(query, db_params):
    try:
        connection = pymysql.connect(**db_params)
        cursor = connection.cursor()
        cursor.execute(query)
        cursor.close()
        connection.commit()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    teardown()
