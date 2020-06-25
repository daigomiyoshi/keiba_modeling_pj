SELECT 
    race_id
    , horse_num
    , bracket_num
    , href_to_horse
    , horse_age
    , horse_sex
    , CAST(weight_penalty AS FLOAT) AS weight_penalty
    , ROUND(CAST(weight_penalty AS FLOAT) - AVG(CAST(weight_penalty AS FLOAT)) OVER (PARTITION BY race_id), 2) AS weight_penalty_diff_from_avg
    , href_to_jockey
    , href_to_owner
    , CAST(popularity_order AS SIGNED) AS popularity_order
    , CAST(win_odds AS FLOAT) AS win_odds
FROM race_table_info
WHERE 0=0
AND win_odds <> 0
;