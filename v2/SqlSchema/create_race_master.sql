CREATE TABLE race_master (
  `race_id` varchar(15) NOT NULL,
  `race_title` varchar(50) DEFAULT NULL,
  `race_coure` varchar(50) DEFAULT NULL,
  `race_weather` varchar(10) DEFAULT NULL,
  `race_condition` varchar(10) DEFAULT NULL,
  `race_year` int DEFAULT NULL,
  `race_month` int DEFAULT NULL,
  `race_date` int DEFAULT NULL,
  `race_dow` varchar(5) DEFAULT NULL,
  `starting_time` varchar(10) DEFAULT NULL,
  `race_info_1` varchar(100) DEFAULT NULL,
  `race_info_2` varchar(100) DEFAULT NULL,
  `race_info_3` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`race_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;