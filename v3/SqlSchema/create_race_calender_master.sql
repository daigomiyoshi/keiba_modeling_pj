CREATE TABLE `race_calender_master` (
  `race_year` int(11) NOT NULL,
  `race_place_id` int(11) NOT NULL,
  `race_kai` int(11) NOT NULL,
  `race_nichi` int(11) NOT NULL,
  `race_round` int(11) NOT NULL,
  `race_month` int(11) NOT NULL,
  `race_date` int(11) NOT NULL,
  PRIMARY KEY (`race_year`,`race_place_id`,`race_kai`,`race_nichi`,`race_round`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;