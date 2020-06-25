import os
import sys
import pandas as pd
import pymysql

this_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(this_dir)
sys.path.append(parent_dir)
from Config import db_config
from Utils.bulk_insert import BulkInsert
from Utils import teardown_tables


def main():
    db_params = db_config.db_params
    con = pymysql.connect(**db_params)

    csv_file_path_list = [
        'tips/race_calendar_master_1986_to_2019.csv', 
        'tips/race_calendar_master_2020.csv'
    ]
    race_calendar_master = read_csv_as_dataframe(csv_file_path_list)
    print('Race calendar (row, col):', race_calendar_master.shape)
    teardown_tables.teardown(['race_calendar_master'])
    bulk_insert(
        con, 
        race_calendar_master.values.tolist(), 
        'race_calendar_master',
        list(race_calendar_master)
    )
    print('Insert is done.')


def read_csv_as_dataframe(csv_file_path_list):
    if len(csv_file_path_list) == 1:
        return pd.read_csv(csv_file_path_list[0])
    else:
        df = pd.read_csv(csv_file_path_list[0])
        for i in range(1, len(csv_file_path_list)):
            tmp = pd.read_csv(csv_file_path_list[i])
            df = pd.concat([df, tmp])
        return df
    
def bulk_insert(con, insert_list, target_table_name, insert_col_names):
    try:
        bi = BulkInsert(con)
        bi.execute(
            insert_data=insert_list,
            target_table=target_table_name,
            col_names=insert_col_names
        )
    except RuntimeError as e:
        print(e)
        raise TypeError


if __name__ == "__main__":
    main()
