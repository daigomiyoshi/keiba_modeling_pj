-- レース毎に、人気上位Nの馬だけに100円複勝を投資する戦略
-- 回収率(2020年以降): 
	-- 上位1位: 約-19%
	-- 上位2位: 約-17%
	-- 上位3位: 約-16.8%
-- 回収率(通年): 
	-- 上位1位: 約-17%
	-- 上位2位: 約-17%
	-- 上位3位: 約-17%

WITH id_tab AS (
	SELECT race_id
	FROM race_master AS m
	WHERE (m.race_year=2020 AND m.race_month>=1)
)
, win_odds_tab AS (
	SELECT race_id
	, horse_num
	, MIN(win_odds) AS win_odds
	FROM race_table_info
	WHERE popularity_order IN (1, 2, 3)
	GROUP BY race_id, horse_num
), refund_tab AS (
	SELECT race_id
	, horse_num
	, MIN(refund_yen) AS refund_yen
	FROM race_refund_info
	WHERE refund_type = '複勝'
	GROUP BY race_id, horse_num
)
, agg_tab AS (
	SELECT a.race_id, b.horse_num, b.win_odds, c.arrival_order, d.refund_yen
	FROM id_tab AS a
	LEFT OUTER JOIN win_odds_tab AS b
	ON a.race_id = b.race_id
	LEFT OUTER JOIN race_result_info AS c
	ON a.race_id = c.race_id AND b.horse_num = c.horse_num
	LEFT OUTER JOIN refund_tab AS d
	ON a.race_id = d.race_id AND b.horse_num = d.horse_num
)
SELECT 
COUNT(race_id)*100 AS '投資額'
, SUM(refund_yen) AS '収益額'
, SUM(refund_yen) - COUNT(race_id)*100 AS '利益額'
, (SUM(refund_yen) - COUNT(race_id)*100) / (COUNT(race_id)*100) AS '回収率'
FROM agg_tab
;
