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
;