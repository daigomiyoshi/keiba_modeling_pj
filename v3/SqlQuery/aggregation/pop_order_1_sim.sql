-- レース毎に、人気=1の馬だけに100円単勝を投資する戦略
-- 回収率 = 約-23%

WITH id_tab AS (
	SELECT race_id
	FROM race_master AS m
	WHERE (m.race_year=2019 AND m.race_month>=5) OR (m.race_year=2020 AND m.race_month>=1)
)
, win_odds_tab AS (
	SELECT race_id
	, MIN(horse_num) AS horse_num
	, MIN(win_odds) AS win_odds
	FROM race_table_info
	WHERE popularity_order = 1
	GROUP BY race_id
), refund_tab AS (
	SELECT race_id
	, MIN(horse_num) AS horse_num
	, MIN(refund_yen) AS refund_yen
	FROM race_refund_info
	WHERE refund_type = '単勝'
	GROUP BY race_id
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
