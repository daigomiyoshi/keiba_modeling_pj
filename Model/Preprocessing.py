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
        joblib.dump(ce, self.parameters['FILE_NAME_OF_HORSE_CATEGORY_ENCODERS'])

        df_ce = ce.transform(df)
        df_ce = df_ce.rename(columns={'href_to_the_horse': 'href_to_the_horse_encoded'})
        return pd.concat([df, df_ce['href_to_the_horse_encoded']], axis=1)

    @staticmethod
    def _get_horse_age_and_sex(x):
        horse_sex = re.split('([ぁ-んァ-ン 一-龥]+)([0-9]+)', x)[1]
        horse_age = int(re.split('([ぁ-んァ-ン 一-龥]+)([0-9]+)', x)[2])
        return pd.Series([horse_sex, horse_age])

    @staticmethod
    def _encode_horse_sex(df):
        horse_sex_mapping = {'牡': 1, '牝': 2, 'セ': 3}
        return df['horse_sex'].map(horse_sex_mapping)

    def preprocess_horse_sex_age(self, df):
        df[['horse_sex', 'horse_age']] = df['horse_sex_age'].apply(self._get_horse_age_and_sex)
        df['horse_sex_encoded'] = self._encode_horse_sex(df)
        return df

    @staticmethod
    def _parse_horse_weight_increment(x):
        return int(x.replace('＋', '+').replace('－', '-').replace('---', '0'))

    def _get_horse_weight_info(self, x):
        horse_weight = int(re.split('(\()(.*)(\))', x)[0])
        horse_weight_increment_str = re.split('(\()(.*)(\))', x)[2]
        horse_weight_increment = self._parse_horse_weight_increment(horse_weight_increment_str)
        return pd.Series([horse_weight, horse_weight_increment])

    def preprocess_horse_weight_and_increment(self, df):
        df[['horse_weight', 'horse_weight_increment']] = \
            df['horse_weight_and_increment'].apply(self._get_horse_weight_info)
        return df

    @staticmethod
    def _get_and_encode_weight_loss_flg(x):
        try:
            weight_loss_flg = re.search('▲|△|☆', x).group()
            weight_loss_encode = int(weight_loss_flg.replace('▲', '3').replace('△', '2').replace('☆', '1'))
        except AttributeError:
            weight_loss_encode = 0
        return weight_loss_encode

    def preprocess_jockey_name(self, df):
        df['weight_loss_encode'] = df['jockey_name'].apply(self._get_and_encode_weight_loss_flg)
        return df

    def encode_fit_and_transform_href_to_the_jockey(self, df):
        if self.parameters['HYPER_PARAMETERS']['CATEGORY_ENCODERS_FOR_JOCKEY'] == 'TargetEncoder':
            ce = category_encoders.TargetEncoder(cols=['href_to_the_jockey'])
        elif self.parameters['HYPER_PARAMETERS']['CATEGORY_ENCODERS_FOR_JOCKEY'] == 'OrdinalEncoder':
            ce = category_encoders.OrdinalEncoder(cols=['href_to_the_jockey'])

        ce.fit(df, df[self.parameters['DATAFRAME_COL_NAMES']['target_col']],
               handle_unknown=self.parameters['HYPER_PARAMETERS']['CATEGORY_ENCODERS_HANDLE_UNKNOWN'])
        joblib.dump(ce, self.parameters['FILE_NAME_OF_JOCKEY_CATEGORY_ENCODERS'])

        df_ce = ce.transform(df)
        df_ce = df_ce.rename(columns={'href_to_the_jockey': 'href_to_the_jockey_encoded'})
        return pd.concat([df, df_ce['href_to_the_jockey_encoded']], axis=1)

    @staticmethod
    def _get_trainer_belonging(x):
        return re.split('\[(.*)\]', x)[1]

    @staticmethod
    def _encode_trainer_belonging(df):
        trainer_belonging_mapping = {'美': 1, '栗': 2, '招': 3}
        return df['trainer_belonging'].map(trainer_belonging_mapping)

    def preprocess_trainer_name(self, df):
        df['trainer_belonging'] = df['trainer_name'].apply(self._get_trainer_belonging)
        df['trainer_belonging_encoded'] = self._encode_trainer_belonging(df)
        return df

    def encode_fit_and_transform_href_to_the_trainer(self, df):
        if self.parameters['HYPER_PARAMETERS']['CATEGORY_ENCODERS_FOR_TRAINER'] == 'TargetEncoder':
            ce = category_encoders.TargetEncoder(cols=['href_to_the_trainer'])
        elif self.parameters['HYPER_PARAMETERS']['CATEGORY_ENCODERS_FOR_TRAINER'] == 'OrdinalEncoder':
            ce = category_encoders.OrdinalEncoder(cols=['href_to_the_trainer'])

        ce.fit(df, df[self.parameters['DATAFRAME_COL_NAMES']['target_col']],
               handle_unknown=self.parameters['HYPER_PARAMETERS']['CATEGORY_ENCODERS_HANDLE_UNKNOWN'])
        joblib.dump(ce, self.parameters['FILE_NAME_OF_TRAINER_CATEGORY_ENCODERS'])

        df_ce = ce.transform(df)
        df_ce = df_ce.rename(columns={'href_to_the_trainer': 'href_to_the_trainer_encoded'})
        return pd.concat([df, df_ce['href_to_the_trainer_encoded']], axis=1)