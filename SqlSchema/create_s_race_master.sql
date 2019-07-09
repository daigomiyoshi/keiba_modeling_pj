CREATE TABLE `s_race_master` (
  `race_id` varchar(10) NOT NULL,
  `race_timing` varchar(50) DEFAULT NULL,
  `race_title` varchar(50) DEFAULT NULL,
  `race_weather` varchar(2) DEFAULT NULL,
  `race_condition` varchar(2) DEFAULT NULL,
  `course_syokin_list` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`race_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;