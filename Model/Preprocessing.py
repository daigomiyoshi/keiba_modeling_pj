import re
import datetime
import pymysql
import pandas as pd


class Preprocessing(object):

    def __init__(self, parameters):
        self.parameters = parameters

    def _get_year_month_day_from_race_timing(x):
        date_str = re.match('([0-9]+)/([0-9]+)/([0-9]+)', x).group()
        year = datetime.datetime.strptime(date_str, '%Y/%m/%d').year
        month = datetime.datetime.strptime(date_str, '%Y/%m/%d').month
        day = datetime.datetime.strptime(date_str, '%Y/%m/%d').day

        return pd.Series([year, month, day])
