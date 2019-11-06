CREATE TABLE `race_calender_master` (
  `race_year` int NOT NULL,
  `race_place_id` int NOT NULL,
  `race_kai` int NOT NULL,
  `race_nichi` int NOT NULL,
  `race_round` int NOT NULL,
  PRIMARY KEY (`race_year`,`race_place_id`,`race_kai`,`race_nichi`,`race_round`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;