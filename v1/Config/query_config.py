queries = {
    'TRAINING_DATA_FROM_MASTER_PRIOR_RESULT':
        '''
        SELECT 
            A.race_id
            , A.race_timing
            , A.race_title
            , A.race_weather
            , A.race_condition
            , A.course_syokin_list
            
            , B.post_position
            , B.horse_number
            , B.href_to_the_horse
            
            , B.horse_age AS horse_sex_age_in_result
            , C.horse_age AS horse_age_in_prior
            , C.horse_sex AS horse_sex_in_prior
            
            , B.horse_weight AS horse_weight_in_result
            , C.horse_weight AS horse_weight_in_prior
            , C.horse_weight_increment_from_previous AS horse_weight_increment_in_prior
            
            , B.horse_impost AS horse_impost_in_result
            , B.jockey_name AS jockey_name_in_result
            , C.jockey_name AS jockey_name_and_horse_impost_in_prior
            
            , B.href_to_the_jockey
            , B.popularity_order
            , B.win_odds
            
            , B.trainer_name AS trainer_name_in_result
            , C.trainer_name AS trainer_name_in_prior
                        
            , C.href_to_the_owner
            , C.breeder_name
            , C.jockey_finish_first_second
            , C.horse_number_finish_first_second
            , C.stallion_finish_first_second
            , C.conbi_finish_first_second
            , C.zensou_info_list
            
            , CAST(B.arrival_order AS SIGNED) AS arrival_order
        FROM keibalab_race_master AS A
        LEFT OUTER JOIN 
            keibalab_race_result_list AS B
        ON A.race_id = B.race_id
        LEFT OUTER JOIN
            keibalab_race_prior_info_list AS C
        ON B.race_id = C.race_id
        AND B.horse_number = C.horse_number
        WHERE B.arrival_order NOT IN ('中止', '除外', '取消', '0', 0)
        AND B.horse_weight <> '計不(---)';
        ''',

    'DATA_TO_PREDICT_FROM_MASTER_PRIOR':
        '''
        SELECT 
            A.race_id
            , A.race_timing
            , A.race_title
            , A.race_weather
            , A.race_condition
            , A.course_syokin_list
            , C.post_position
            , C.horse_number
            , C.href_to_the_horse
            , C.horse_age AS horse_age_in_prior
            , C.horse_sex AS horse_sex_in_prior
            , C.horse_weight AS horse_weight_in_prior
            , C.horse_weight_increment_from_previous AS horse_weight_increment_in_prior
            , C.jockey_name AS jockey_name_and_horse_impost_in_prior
            , C.href_to_the_jockey
            , C.popularity_order
            , C.win_odds
            , C.trainer_name AS trainer_name_in_prior
            , C.href_to_the_owner
            , C.breeder_name
            , C.jockey_finish_first_second
            , C.horse_number_finish_first_second
            , C.stallion_finish_first_second
            , C.conbi_finish_first_second
            , C.zensou_info_list
        FROM keibalab_race_master AS A
        LEFT OUTER JOIN
            keibalab_race_prior_info_list AS C
        ON A.race_id = C.race_id
        WHERE C.popularity_order <> 0;
        '''
}
