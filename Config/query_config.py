queries = {
    'RACE_PRIOR_INFO_FOR_TRAINING':
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
            , C.horse_age AS horse_sex_age
            , C.horse_weight AS horse_weight_and_increment
            , C.horse_impost
            , C.jockey_name
            , C.href_to_the_jockey
            , C.popularity_order
            , C.win_odds
            , C.trainer_name
            , C.href_to_the_trainer
            , B.href_to_the_owner
            , B.breeder_name
            , B.jockey_finish_first_second
            , B.horse_number_finish_first_second
            , B.stallion_finish_first_second
            , B.conbi_finish_first_second
            , B.zensou_info_list
            , CAST(C.arrival_order AS SIGNED) AS arrival_order
        FROM keibalab_race_master AS A
        LEFT OUTER JOIN 
            keibalab_race_prior_info_list AS B
        ON A.race_id = B.race_id
        LEFT OUTER JOIN
            keibalab_race_result_list AS C
        ON B.race_id = C.race_id
        AND B.horse_number = C.horse_number
        WHERE C.arrival_order NOT IN ('中止', '除外', '取消', '0');
        '''
}
