-- レース毎に、人気=Xの馬だけに100円単勝を投資する戦略
-- 5-7位は利益率が約-18%と、少し高くなる

	-- 1	4220600	3256550	-964050	-0.2284
	-- 2	4220100	3332550	-887550	-0.2103
	-- 3	4220600	3439700	-780900	-0.1850
	-- 4	4220100	3354690	-865410	-0.2051
	-- 5	4220600	3427810	-792790	-0.1878
	-- 6	4217500	3471500	-746000	-0.1769
	-- 7	4208900	3419690	-789210	-0.1875
	-- 8	4180700	3284340	-896360	-0.2144
	-- 9	4104200	3084220	-1019980 -0.2485
	-- 10	3973200	2912670	-1060530 -0.2669
	-- 11	3786800	2735090	-1051710 -0.2777
	-- 12	3548400	2379180	-1169220 -0.3295
	-- 13	3227100	1992860	-1234240 -0.3825
	-- 14	2878400	1417290	-1461110 -0.5076
	-- 15	2444600	1259610	-1184990 -0.4847
	-- 16	1904700	746000	-1158700 -0.6083
	-- 17	431200	106030	-325170	-0.7541
	-- 18	346600	59520	-287080	-0.8283

WITH id_tab AS (
	SELECT race_id
	, CAST(SUBSTRING(race_id, 5, 2) AS SIGNED) AS race_place
	FROM race_master AS m
-- 	WHERE (m.race_year=2020 AND m.race_month>=1)
)
, win_odds_tab AS (
	SELECT race_id
	, popularity_order
	, MIN(horse_num) AS horse_num
	, MIN(win_odds) AS win_odds
	FROM race_table_info
	GROUP BY race_id, popularity_order
), refund_tab AS (
	SELECT race_id
	, MIN(horse_num) AS horse_num
	, MIN(refund_yen) AS refund_yen
	FROM race_refund_info
	WHERE refund_type = '単勝'
	GROUP BY race_id
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
)
SELECT 
popularity_order
, COUNT(race_id)*100 AS '投資額'
, SUM(refund_yen) AS '収益額'
, SUM(refund_yen) - COUNT(race_id)*100 AS '利益額'
, (SUM(refund_yen) - COUNT(race_id)*100) / (COUNT(race_id)*100) AS '回収率'
FROM agg_tab
WHERE popularity_order NOT IN ('**', '--')
GROUP BY popularity_order
ORDER BY popularity_order;