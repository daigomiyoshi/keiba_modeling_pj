import re
import datetime
import numpy as np
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
    def _encode_dow(df):
        dow_mapping = {'土': 1, '日': 2}
        return df['dow'].map(dow_mapping)

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
        df['dow_encoded'] = self._encode_dow(df)
        df['race_course'] = df['race_timing'].apply(self._get_racecourse_from_race_timing)
        df['race_course_encoded'] = self._encode_race_course(df)
        df['time_in_racecourse'] = df['race_timing'].apply(self._get_time_in_the_racecourse_from_race_timing)
        df['what_day_in_racecourse'] = df['race_timing'].apply(self._get_what_day_in_the_racecourse_from_race_timing)
        return df

    @staticmethod
    def encode_race_weather(df):
        race_weather_mapping = {'晴': 1, '曇': 2, '小雨': 3, '雨': 4, '小雪': 5, '雪': 6, 'unknown': 7}
        df['race_weather_encoded'] = df['race_weather'].map(race_weather_mapping)
        return df

    @staticmethod
    def encode_race_condition(df):
        race_condition_mapping = {'良': 1, '稍': 2, '重': 3, '不': 4, 'unknown': 5}
        df['race_condition_encoded'] = df['race_condition'].map(race_condition_mapping)
        return df

    def encode_fit_and_transform_href_to_the_horse(self, df):
        if self.parameters['HYPER_PARAMETERS']['CATEGORY_ENCODERS_FOR_HORSE'] == 'TargetEncoder':
            ce = category_encoders.TargetEncoder(cols=['href_to_the_horse'])
        elif self.parameters['HYPER_PARAMETERS']['CATEGORY_ENCODERS_FOR_HORSE'] == 'OrdinalEncoder':
            ce = category_encoders.OrdinalEncoder(cols=['href_to_the_horse'])

        ce.fit(df, df['arrival_order'],
               handle_unknown=self.parameters['HYPER_PARAMETERS']['CATEGORY_ENCODERS_HANDLE_UNKNOWN'])
        joblib.dump(ce, self.parameters['FILE_NAME_OF_HORSE_CATEGORY_ENCODERS'])

        df_ce = ce.transform(df)
        df_ce = df_ce.rename(columns={'href_to_the_horse': 'href_to_the_horse_encoded'})
        return pd.concat([df, df_ce['href_to_the_horse_encoded']], axis=1)

    @staticmethod
    def _get_horse_age_and_sex_in_result(x):
        horse_sex = re.split('([ぁ-んァ-ン 一-龥]+)([0-9]+)', x)[1]
        horse_age = int(re.split('([ぁ-んァ-ン 一-龥]+)([0-9]+)', x)[2])
        return pd.Series([horse_sex, horse_age])

    @staticmethod
    def _encode_horse_sex(df):
        horse_sex_mapping = {'牡': 1, '牝': 2, 'セ': 3}
        return df.map(horse_sex_mapping)

    def preprocess_horse_sex_age(self, df, target_cols_type):
        if target_cols_type == 'result':
            df[['horse_sex', 'horse_age']] = df['horse_sex_age_in_result'].apply(self._get_horse_age_and_sex_in_result)
            df['horse_sex_encoded'] = self._encode_horse_sex(df['horse_sex'])
        elif target_cols_type == 'prior':
            df['horse_age'] = pd.to_numeric(df["horse_age_in_prior"], errors='coerce')
            df['horse_sex_encoded'] = self._encode_horse_sex(df['horse_sex_in_prior'])
        return df

    @staticmethod
    def _parse_horse_weight_increment(x):
        return int(x.replace('＋', '+').replace('－', '-').replace('---', '0'))

    def _get_horse_weight_info_in_result(self, x):
        horse_weight = int(re.split('(\()(.*)(\))', x)[0])
        horse_weight_increment_str = re.split('(\()(.*)(\))', x)[2]
        horse_weight_increment = self._parse_horse_weight_increment(horse_weight_increment_str)
        return pd.Series([horse_weight, horse_weight_increment])

    @staticmethod
    def _get_horse_weight_in_prior(x):
        try:
            return int(re.search("[0-9]+", x).group())
        except TypeError:
            return np.nan

    def _get_horse_weight_increment_in_prior(self, x):
        try:
            horse_weight_increment_str = re.split('(\()(.*)(kg\))', x)[2]
            horse_weight_increment = self._parse_horse_weight_increment(horse_weight_increment_str)
            return horse_weight_increment
        except TypeError:
            return np.nan

    def preprocess_horse_weight_and_increment(self, df, target_cols_type):
        if target_cols_type == 'result':
            df[['horse_weight', 'horse_weight_increment']] = df['horse_weight_in_result'].apply(
                self._get_horse_weight_info_in_result)
        elif target_cols_type == 'prior':
            df['horse_weight'] = df['horse_weight_in_prior'].apply(self._get_horse_weight_in_prior)
            df['horse_weight_increment'] = df['horse_weight_increment_in_prior'].apply(
                self._get_horse_weight_increment_in_prior)
        return df

    @staticmethod
    def _get_and_encode_weight_loss_flg(x):
        try:
            weight_loss_flg = re.search('▲|△|☆', x).group()
            weight_loss_encode = int(weight_loss_flg.replace('▲', '3').replace('△', '2').replace('☆', '1'))
        except AttributeError:
            weight_loss_encode = 0
        return weight_loss_encode

    @staticmethod
    def _get_horse_impost_in_prior(x):
        try:
            return float(re.split('(▲|△|☆|.)(.*)(\()(.*)(\))(.*)', x)[4])
        except TypeError:
            return np.nan

    def _get_weight_loss_encode_in_prior(self, x):
        try:
            weight_loss_flg_str = re.split('(▲|△|☆|.)(.*)(\()(.*)(\))(.*)', x)[1]
            return self._get_and_encode_weight_loss_flg(weight_loss_flg_str)
        except TypeError:
            return np.nan

    def preprocess_jockey_name(self, df, target_cols_type):
        if target_cols_type == 'result':
            df['horse_impost'] = df['horse_impost_in_result']
            df['weight_loss_encode'] = df['jockey_name_in_result'].apply(
                self._get_and_encode_weight_loss_flg)
        elif target_cols_type == 'prior':
            df['horse_impost'] = df['jockey_name_and_horse_impost_in_prior'].apply(self._get_horse_impost_in_prior)
            df['weight_loss_encode'] = df['jockey_name_and_horse_impost_in_prior'].apply(
                self._get_weight_loss_encode_in_prior)
        return df

    def encode_fit_and_transform_href_to_the_jockey(self, df):
        if self.parameters['HYPER_PARAMETERS']['CATEGORY_ENCODERS_FOR_JOCKEY'] == 'TargetEncoder':
            ce = category_encoders.TargetEncoder(cols=['href_to_the_jockey'])
        elif self.parameters['HYPER_PARAMETERS']['CATEGORY_ENCODERS_FOR_JOCKEY'] == 'OrdinalEncoder':
            ce = category_encoders.OrdinalEncoder(cols=['href_to_the_jockey'])

        ce.fit(df, df['arrival_order'],
               handle_unknown=self.parameters['HYPER_PARAMETERS']['CATEGORY_ENCODERS_HANDLE_UNKNOWN'])
        joblib.dump(ce, self.parameters['FILE_NAME_OF_JOCKEY_CATEGORY_ENCODERS'])

        df_ce = ce.transform(df)
        df_ce = df_ce.rename(columns={'href_to_the_jockey': 'href_to_the_jockey_encoded'})
        return pd.concat([df, df_ce['href_to_the_jockey_encoded']], axis=1)

    @staticmethod
    def _get_trainer_belonging_in_result(x):
        return re.split('\[(.*)\]', x)[1]

    @staticmethod
    def _get_trainer_belonging_in_prior(x):
        try:
            return re.split('(.*)(・)(.*)', x)[1]
        except TypeError:
            return np.nan

    @staticmethod
    def _encode_trainer_belonging(df):
        trainer_belonging_mapping = {'美': 1, '栗': 2, '招': 3}
        return df['trainer_belonging'].map(trainer_belonging_mapping)

    def preprocess_trainer_name(self, df, target_cols_type):
        if target_cols_type == 'result':
            df['trainer_belonging'] = df['trainer_name_in_result'].apply(self._get_trainer_belonging_in_result)
            df['trainer_belonging_encoded'] = self._encode_trainer_belonging(df)
        elif target_cols_type == 'prior':
            df['trainer_belonging'] = df['trainer_name_in_prior'].apply(self._get_trainer_belonging_in_prior)
            df['trainer_belonging_encoded'] = self._encode_trainer_belonging(df)
        return df

    def encode_fit_and_transform_href_to_the_trainer(self, df):
        if self.parameters['HYPER_PARAMETERS']['CATEGORY_ENCODERS_FOR_TRAINER'] == 'TargetEncoder':
            ce = category_encoders.TargetEncoder(cols=['href_to_the_trainer'])
        elif self.parameters['HYPER_PARAMETERS']['CATEGORY_ENCODERS_FOR_TRAINER'] == 'OrdinalEncoder':
            ce = category_encoders.OrdinalEncoder(cols=['href_to_the_trainer'])

        ce.fit(df, df['arrival_order'],
               handle_unknown=self.parameters['HYPER_PARAMETERS']['CATEGORY_ENCODERS_HANDLE_UNKNOWN'])
        joblib.dump(ce, self.parameters['FILE_NAME_OF_TRAINER_CATEGORY_ENCODERS'])

        df_ce = ce.transform(df)
        df_ce = df_ce.rename(columns={'href_to_the_trainer': 'href_to_the_trainer_encoded'})
        return pd.concat([df, df_ce['href_to_the_trainer_encoded']], axis=1)

    def _categorize_arrival_order(self, x):
        if x == 1:
            arrival_order_category = self.parameters['MODEL_TARGET_RANK_LABEL']['first']
        elif x == 2:
            arrival_order_category = self.parameters['MODEL_TARGET_RANK_LABEL']['second']
        elif x == 3:
            arrival_order_category = self.parameters['MODEL_TARGET_RANK_LABEL']['third']
        else:
            arrival_order_category = self.parameters['MODEL_TARGET_RANK_LABEL']['others']
        return arrival_order_category

    def preprocess_arrival_order(self, df):
        df['arrival_order_category'] = df['arrival_order'].apply(self._categorize_arrival_order)
        return df
