queries = {
    'RACE_MASTER_INFO':
        '''
        SELECT 
            race_id
            , CAST(SUBSTRING(race_id, 11, 12) AS SIGNED) AS race_round
            , CAST(SUBSTRING(race_info_1, 1, 1) AS SIGNED) AS race_kai
            , SUBSTRING(race_info_1, 3, 2) AS race_place
            , SUBSTRING(race_course, 1, 1) AS race_course_baba
            , CAST(SUBSTRING(race_course, 2, 4) AS SIGNED) AS race_course_dist
            , SUBSTRING(race_course, LOCATE('(',race_course)+1, LOCATE(')',race_course)- LOCATE('(',race_course)-1) AS race_course_mawari
            , race_weather
            , race_condition
            , race_year
            , race_month
            , race_date
            , race_dow
            , CAST(SUBSTRING(starting_time, 1, 2) AS SIGNED) AS starting_hour
            , CAST(SUBSTRING(starting_time, 4, 5) AS SIGNED) AS starting_minutes
        FROM race_master
        ''',

    'RACE_TABLE_RESULT_INFO':
        '''
        SELECT 
            A.race_id
            , A.horse_num
            , A.bracket_num
            , A.href_to_horse
            , A.horse_age
            , A.horse_sex
            , CAST(A.weight_penalty AS FLOAT) AS weight_penalty
            , A.href_to_jockey
            , A.href_to_owner
            , CAST(A.popularity_order AS SIGNED) AS popularity_order
            , CAST(A.win_odds AS FLOAT) AS win_odds
            , CASE WHEN B.arrival_order <> 1 THEN 
              CAST(ROUND(TIMEDIFF(B.arrival_time, FIRST_VALUE(B.arrival_time) OVER (PARTITION BY B.race_id ORDER BY CAST(B.arrival_order AS SIGNED)))/60, 3) AS FLOAT) 
              ELSE 0.000 END AS arrival_sec_diff_from_first
            , CAST(B.arrival_order AS SIGNED) AS arrival_order
        FROM race_table_info AS A
        LEFT JOIN race_result_info AS B
        ON A.race_id = B.race_id
        AND A.horse_num = B.horse_num
        WHERE 0=0
        AND CAST(B.arrival_order AS SIGNED) NOT IN ('', 0)
        AND A.win_odds <> 0
        ''',

    'RACE_PAST_X_RESULT_INFO':
        '''
        SELECT 
            DISTINCT A.race_id
            , A.horse_num
            , CAST(A.past_x AS SIGNED) AS past_x
            , CAST(A.arrival_order AS SIGNED) AS past_x_arrival_order
            , CAST(B.arrival_sec_diff_from_first AS FLOAT)  AS arrival_sec_diff_from_first
        FROM race_past_5_result_info AS A
        INNER JOIN (
            SELECT *
            , ROUND(TIMEDIFF(arrival_time, FIRST_VALUE(arrival_time) OVER (PARTITION BY race_id ORDER BY arrival_order))/60, 3) AS arrival_sec_diff_from_first
            FROM race_result_info
            WHERE CAST(arrival_order AS SIGNED) NOT IN ('', 0)
        ) AS B
        ON A.past_x_race_id = B.race_id
        AND A.arrival_order = B.arrival_order
        WHERE 0=0
        AND CAST(A.arrival_order AS SIGNED) NOT IN ('', 0)
        AND A.past_x_race_id <> '201008060411'
        ''',

    'PREDICTION_SCORE_AND_RESULT_INFO':
        '''
        SELECT 
              C.race_id
            , C.race_title
            , C.race_year
            , C.race_month
            , C.race_date
            , C.race_dow
            , C.starting_time
            , A.horse_num
            , A.predicted_score
            , CASE WHEN B.refund_type IS NULL THEN '4着以降' ELSE B.refund_type END AS refund_type
            , CASE WHEN B.refund_yen IS NULL THEN '4着以降' ELSE B.refund_yen END AS refund_yen
            , CASE WHEN B.popularity_order IS NULL THEN '4着以降' ELSE B.popularity_order END AS popularity_order
        FROM race_predicted_score AS A
        LEFT JOIN race_refund_info AS B
        ON A.race_id = B.race_id
        AND A.horse_num = B.horse_num
        LEFT JOIN race_master AS C
        ON A.race_id = C.race_id
        ORDER BY C.race_year, C.race_month, C.race_date, A.race_id, A.horse_num
        '''
}
