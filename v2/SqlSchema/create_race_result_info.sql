CREATE TABLE race_result_info (
  `race_id` varchar(15) NOT NULL,
  `bracket_num` int(11) NOT NULL,
  `horse_num` int(11) NOT NULL,
  `arrival_time` varchar(10) DEFAULT NULL,
  `arrival_diff` varchar(20) DEFAULT NULL,
  `arrrival_order` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`race_id`,`horse_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;