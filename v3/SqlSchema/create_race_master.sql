CREATE TABLE `race_master` (
  `race_id` varchar(15) NOT NULL,
  `race_title` varchar(50) DEFAULT NULL,
  `race_course` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `race_weather` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `race_condition` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `race_year` int(11) DEFAULT NULL,
  `race_month` int(11) DEFAULT NULL,
  `race_date` int(11) DEFAULT NULL,
  `race_dow` varchar(5) DEFAULT NULL,
  `starting_time` varchar(10) DEFAULT NULL,
  `race_other_info` varchar(1000) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  PRIMARY KEY (`race_id`),
  KEY `race_id` (`race_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;