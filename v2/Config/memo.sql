-- 過去の成績(馬柱5走)
SELECT A.*, B.arrival_time, B.arrival_diff, B.arrival_sec_diff_from_first
FROM race_past_5_result_info AS A
LEFT OUTER JOIN (
SELECT *
, ROUND(TIMEDIFF(arrival_time, FIRST_VALUE(arrival_time) OVER (PARTITION BY race_id ORDER BY arrival_order))/60, 3) AS arrival_sec_diff_from_first
FROM race_result_info
WHERE arrival_order <> ''
ORDER BY race_id, arrival_time
) AS B
ON A.past_x_race_id = B.race_id
AND A.arrival_order = B.arrival_order
;

-- 単勝の回収率
SELECT COUNT(1)
, AVG(CASE WHEN popularity_order = 1 THEN refund_yen ELSE 0 END) AS '回収率'
FROM race_refund_info
WHERE refund_type = '単勝'
;

-- 人気度毎の回収率
SELECT 
CAST(A.popularity_order AS SIGNED) AS popularity_order
, AVG(CASE WHEN B.refund_yen IS NULL THEN 0 ELSE B.refund_yen END) AS collection_rate
FROM race_table_info AS A
LEFT OUTER JOIN (SELECT * FROM race_refund_info WHERE refund_type = '単勝' LIMIT 100000) AS B
ON  A.race_id = B.race_id
AND A.horse_num = B.horse_num 
WHERE A.popularity_order <> 0
GROUP BY A.popularity_order
ORDER BY CAST(A.popularity_order AS SIGNED)
;

-- 馬齢毎の回収率
SELECT 
CAST(A.horse_age AS SIGNED) AS horse_age
, AVG(CASE WHEN B.refund_yen IS NULL THEN 0 ELSE B.refund_yen END) AS collection_rate
FROM race_table_info AS A
LEFT OUTER JOIN (SELECT * FROM race_refund_info WHERE refund_type = '単勝' LIMIT 100000) AS B
ON  A.race_id = B.race_id
AND A.horse_num = B.horse_num 
GROUP BY A.horse_age
ORDER BY CAST(A.horse_age AS SIGNED)
;