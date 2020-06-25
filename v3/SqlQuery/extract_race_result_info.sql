SELECT 
    race_id
    , bracket_num
    , horse_num
    , CASE WHEN arrival_order <> 1 THEN 
        CAST(ROUND(TIMEDIFF(arrival_time, FIRST_VALUE(arrival_time) OVER (PARTITION BY race_id ORDER BY CAST(arrival_order AS SIGNED)))/60, 3) AS FLOAT) 
        ELSE 0.000 END AS arrival_sec_diff_from_first
    , CAST(arrival_order AS SIGNED) AS arrival_order
FROM race_result_info
WHERE 0=0
AND CAST(arrival_order AS SIGNED) NOT IN ('', 0)