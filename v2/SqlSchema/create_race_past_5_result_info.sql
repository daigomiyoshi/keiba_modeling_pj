CREATE TABLE `race_past_5_result_info` (
  `race_id` varchar(15) NOT NULL,
  `bracket_num` int(11) NOT NULL,
  `horse_num` int(11) NOT NULL,
  `past_1_order` varchar(5) DEFAULT NULL,
  `past_2_order` varchar(5) DEFAULT NULL,
  `past_3_order` varchar(5) DEFAULT NULL,
  `past_4_order` varchar(5) DEFAULT NULL,
  `past_5_order` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`race_id`,`horse_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
