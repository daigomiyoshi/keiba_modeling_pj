SELECT 
    race_id
    , horse_num
    , COUNT(arrival_order) AS count_of_latest_runs
    , ROUND(AVG(arrival_order), 2) AS avg_arrival_order
    , ROUND(STD(arrival_order), 2) AS std_arrival_order
    , ROUND(MIN(CASE WHEN past_x = 1 THEN arrival_order ELSE NULL END), 2) AS latest_arrival_order
FROM race_past_5_result_info
GROUP BY race_id, horse_num
;