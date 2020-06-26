WITH 
master_mod AS ( 
    SELECT
        race_id
        , CAST(SUBSTRING(race_id, 5, 2) AS SIGNED) AS race_place
        , CAST(SUBSTRING(race_id, 7, 2) AS SIGNED) AS race_kai
        , CAST(SUBSTRING(race_id, 9, 2) AS SIGNED) AS race_nichi
        , CAST(SUBSTRING(race_id, 11, 2) AS SIGNED) AS race_round
        , race_year
        , race_month
        , race_date
        , race_dow
        , SUBSTRING(LTRIM(race_course), 1, 1) AS race_course_baba
        , CAST(SUBSTRING(LTRIM(race_course), 2, 4) AS SIGNED) AS race_course_distance
        , SUBSTRING(race_course, LOCATE('(',race_course)+1, LOCATE(')',race_course)- LOCATE('(',race_course)-1) AS race_course_mawari
        , race_weather
        , race_condition
        , CAST(SUBSTRING(starting_time, 1, 2) AS SIGNED) AS starting_hour
        , CAST(SUBSTRING(starting_time, 4, 5) AS SIGNED) AS starting_minutes
    FROM race_master
), 
table_mod AS (
    SELECT 
        race_id
        , horse_num
        , CASE WHEN horse_num < 10 THEN CONCAT(race_id, '_0', CAST(horse_num AS CHAR)) ELSE CONCAT(race_id, '_', CAST(horse_num AS CHAR)) END AS race_horse_id
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
),
past_5_result_mode AS (
    SELECT 
        race_id
        , horse_num
        , CASE WHEN horse_num < 10 THEN CONCAT(race_id, '_0', CAST(horse_num AS CHAR)) ELSE CONCAT(race_id, '_', CAST(horse_num AS CHAR)) END AS race_horse_id
        , COUNT(arrival_order) AS count_of_latest_runs
        , ROUND(AVG(arrival_order), 2) AS avg_arrival_order
        , ROUND(STD(arrival_order), 2) AS std_arrival_order
        , ROUND(MIN(CASE WHEN past_x = 1 THEN arrival_order ELSE NULL END), 2) AS latest_arrival_order
    FROM race_past_5_result_info
    GROUP BY race_id, horse_num
),
result_mod AS (
    SELECT 
        race_id
        , horse_num
        , CASE WHEN horse_num < 10 THEN CONCAT(race_id, '_0', CAST(horse_num AS CHAR)) ELSE CONCAT(race_id, '_', CAST(horse_num AS CHAR)) END AS race_horse_id
        , bracket_num
        , CASE WHEN arrival_order <> 1 THEN 
            CAST(ROUND(TIMEDIFF(arrival_time, FIRST_VALUE(arrival_time) OVER (PARTITION BY race_id ORDER BY CAST(arrival_order AS SIGNED)))/60, 3) AS FLOAT) 
            ELSE 0.000 END AS arrival_sec_diff_from_first
        , CAST(arrival_order AS SIGNED) AS arrival_order
    FROM race_result_info
    WHERE 0=0
    AND CAST(arrival_order AS SIGNED) NOT IN ('', 0)
), 
refund_mode AS (
	SELECT race_id
	, MIN(horse_num) AS horse_num
	, CASE WHEN MIN(horse_num) < 10 THEN CONCAT(race_id, '_0', CAST(MIN(horse_num) AS CHAR)) ELSE CONCAT(race_id, '_', CAST(MIN(horse_num) AS CHAR)) END AS race_horse_id
	, MIN(refund_yen) AS refund_yen
	FROM race_refund_info
	WHERE refund_type = '単勝'
	GROUP BY race_id
)
SELECT a.race_id
, a.horse_num
, a.race_horse_id
, a.bracket_num
, race_place
, race_kai
, race_nichi
, race_round
, race_year
, race_month
, race_date
, race_dow
, race_course_baba
, race_course_distance
, race_course_mawari
, race_weather
, race_condition
, starting_hour
, starting_minutes
, href_to_horse
, horse_age
, horse_sex
, weight_penalty
, weight_penalty_diff_from_avg
, href_to_jockey
, href_to_owner
, popularity_order
, win_odds
, count_of_latest_runs
, avg_arrival_order
, std_arrival_order
, latest_arrival_order
-- 以下は結果に関する情報
, arrival_order
, arrival_sec_diff_from_first
, CASE WHEN refund_yen IS NOT NULL THEN refund_yen ELSE 0 END AS refund_yen
FROM table_mod AS a
LEFT OUTER JOIN master_mod AS b
ON a.race_id = b.race_id
LEFT OUTER JOIN past_5_result_mode AS c
ON a.race_id = c.race_id AND a.horse_num = c.horse_num
LEFT OUTER JOIN result_mod AS d
ON a.race_id = d.race_id AND a.horse_num = d.horse_num
LEFT OUTER JOIN refund_mode AS e
ON a.race_id = e.race_id AND a.horse_num = e.horse_num
;

