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
            , B.post_position
            , B.horse_number
            , B.href_to_the_horse
            , B.jockey_name
            , B.href_to_the_jockey
            , B.trainer_name
            , B.horse_age
            , B.horse_sex
            , B.popularity_order
            , B.win_odds
            , B.horse_weight
            , B.horse_weight_increment_from_previous
            , B.href_to_the_owner
            , B.breeder_name
            , B.jockey_finish_first_second
            , B.horse_number_finish_first_second
            , B.stallion_finish_first_second
            , B.conbi_finish_first_second
            , B.zensou_info_list
            , C.arrival_order
        FROM keibalab_race_master AS A
        LEFT OUTER JOIN 
            keibalab_race_prior_info_list AS B
        ON A.race_id = B.race_id
        LEFT OUTER JOIN
            keibalab_race_result_list AS C
        ON B.race_id = C.race_id
        AND B.horse_number = C.horse_number
        WHERE C.arrival_order NOT IN ('中止', '除外', '0');
        '''
}
