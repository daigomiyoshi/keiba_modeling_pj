import re
import datetime
import pandas as pd
import category_encoders
import joblib


class Preprocessing(object):

    def __init__(self, parameters):
        self.parameters = parameters

    @staticmethod
    def _get_year_month_day_from_race_timing(x):
        date_str = re.match('([0-9]+)/([0-9]+)/([0-9]+)', x).group()
        year = datetime.datetime.strptime(date_str, '%Y/%m/%d').year
        month = datetime.datetime.strptime(date_str, '%Y/%m/%d').month
        day = datetime.datetime.strptime(date_str, '%Y/%m/%d').day
        return pd.Series([year, month, day])

    @staticmethod
    def _get_dow_from_race_timing(x):
        return re.search("土|日", x).group()

    @staticmethod
    def _get_time_in_the_racecourse_from_race_timing(x):
        return int(re.split('([0-9]+)回([ぁ-んァ-ン 一-龥]+)([0-9]+)日目', x)[1])

    @staticmethod
    def _get_racecourse_from_race_timing(x):
        return re.split('([0-9]+)回([ぁ-んァ-ン 一-龥]+)([0-9]+)日目', x)[2]

    @staticmethod
    def _get_what_day_in_the_racecourse_from_race_timing(x):
        return int(re.split('([0-9]+)回([ぁ-んァ-ン 一-龥]+)([0-9]+)日目', x)[3])

    @staticmethod
    def _encode_race_course(df):
        race_course_mapping = {'函館': 1, '札幌': 2, '福島': 3, '東京': 4, '中山': 5,
                               '新潟': 6, '中京': 7, '阪神': 8, '京都': 9, '小倉': 10}
        return df['race_course'].map(race_course_mapping)

    def preprocess_race_timing(self, df):
        df[['year', 'month', 'day']] = df['race_timing'].apply(self._get_year_month_day_from_race_timing)
        df['dow'] = df['race_timing'].apply(self._get_dow_from_race_timing)
        df['race_course'] = df['race_timing'].apply(self._get_racecourse_from_race_timing)
        df['race_course_encoded'] = self._encode_race_course(df)
        df['time_in_racecourse'] = df['race_timing'].apply(self._get_time_in_the_racecourse_from_race_timing)
        df['what_day_in_racecourse'] = df['race_timing'].apply(self._get_what_day_in_the_racecourse_from_race_timing)
        return df

    @staticmethod
    def encode_race_weather(df):
        race_weather_mapping = {'晴': 1, '曇': 2, '小雨': 3, '雨': 4, '小雪': 5, '雪': 6}
        return df['race_weather'].map(race_weather_mapping)

    @staticmethod
    def encode_race_condition(df):
        race_condition_mapping = {'良': 1, '稍': 2, '重': 3, '不': 4}
        return df['race_condition'].map(race_condition_mapping)

    def encode_fit_and_transform_href_to_the_horse(self, df):
        if self.parameters['HYPER_PARAMETERS']['CATEGORY_ENCODERS_FOR_HORSE'] == 'TargetEncoder':
            ce = category_encoders.TargetEncoder(cols=['href_to_the_horse'])
        elif self.parameters['HYPER_PARAMETERS']['CATEGORY_ENCODERS_FOR_HORSE'] == 'OrdinalEncoder':
            ce = category_encoders.OrdinalEncoder(cols=['href_to_the_horse'])

        ce.fit(df, df[self.parameters['DATAFRAME_COL_NAMES']['target_col']],
               handle_unknown=self.parameters['HYPER_PARAMETERS']['CATEGORY_ENCODERS_HANDLE_UNKNOWN'])
        joblib.dump(ce, self.parameters['FILE_NAME_OF_CATEGORY_ENCODERS'])

        df_te = ce.transform(df)
        df_te = df_te.rename(columns={'href_to_the_horse': 'href_to_the_horse_encoded'})
        return pd.concat([df, df_te['href_to_the_horse_encoded']], axis=1)
