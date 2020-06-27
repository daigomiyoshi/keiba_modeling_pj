-- レース毎に、人気=Xの馬だけに100円複勝を投資する戦略
-- 4位以降は回収率が悪い

	-- 1	4221200	3523280	-697920	-0.1653	83.4663
	-- 2	4220300	3502540	-717760	-0.1701	82.9927
	-- 3	4220700	3482400	-738300	-0.1749	82.5076
	-- 4	4220100	3336780	-883320	-0.2093	79.0687
	-- 5	4220600	3319860	-900740	-0.2134	78.6585
	-- 6	4217600	3381780	-835820	-0.1982	80.1826
	-- 7	4208900	3302280	-906620	-0.2154	78.4595
	-- 8	4180800	3345610	-835190	-0.1998	80.0232
	-- 9	4104200	3130430	-973770	-0.2373	76.2738
	-- 10	3973400	3060870	-912530	-0.2297	77.0340
	-- 11	3786800	2857680	-929120	-0.2454	75.4642
	-- 12	3548600	2500800	-1047800 -0.2953 70.4729
	-- 13	3227100	2165190	-1061910 -0.3291 67.0940
	-- 14	2878400	1765520	-1112880 -0.3866 61.3369
	-- 15	2444600	1351630	-1092970 -0.4471 55.2904
	-- 16	1904800	903860	-1000940 -0.5255 47.4517
	-- 17	431200	180620	-250580	-0.5811	41.8878
	-- 18	346600	145460	-201140	-0.5803	41.9677

WITH id_tab AS (
	SELECT race_id
	, CAST(SUBSTRING(race_id, 5, 2) AS SIGNED) AS race_place
	FROM race_master AS m
-- 	WHERE (m.race_year=2020 AND m.race_month>=1)
)
, win_odds_tab AS (
	SELECT race_id
	, popularity_order
	, horse_num
	, win_odds
	FROM race_table_info
), refund_tab AS (
	SELECT race_id
	, horse_num
	, MIN(refund_yen) AS refund_yen
	FROM race_refund_info
	WHERE refund_type = '複勝'
	GROUP BY race_id, horse_num
)
, agg_tab AS (
	SELECT a.race_id, a.race_place, b.horse_num, b.win_odds
	, CAST(b.popularity_order AS SIGNED) AS popularity_order
	, c.arrival_order, d.refund_yen
	FROM id_tab AS a
	LEFT OUTER JOIN win_odds_tab AS b
	ON a.race_id = b.race_id
	LEFT OUTER JOIN race_result_info AS c
	ON a.race_id = c.race_id AND b.horse_num = c.horse_num
	LEFT OUTER JOIN refund_tab AS d
	ON a.race_id = d.race_id AND b.horse_num = d.horse_num
	WHERE b.popularity_order NOT IN ('**', '--', 0)
)
SELECT
popularity_order
, COUNT(race_id)*100 AS '投資額'
, SUM(refund_yen) AS '収益額'
, SUM(refund_yen) - COUNT(race_id)*100 AS '利益額'
, (SUM(refund_yen) - COUNT(race_id)*100) / (COUNT(race_id)*100) AS '利益率'
, 100 * SUM(refund_yen) / (COUNT(race_id)*100) AS '回収率'
FROM agg_tab
GROUP BY popularity_order
ORDER BY popularity_order;