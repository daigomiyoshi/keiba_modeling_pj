CREATE TABLE `race_table_info` (
  `race_id` varchar(15) NOT NULL,
  `bracket_num` int(11) NOT NULL,
  `horse_num` int(11) NOT NULL,
  `horse_name` varchar(50) DEFAULT NULL,
  `horse_age` int(11) DEFAULT NULL,
  `horse_sex` varchar(5) DEFAULT NULL,
  `weight_penalty` varchar(10) DEFAULT NULL,
  `jockey_name` varchar(10) DEFAULT NULL,
  `href_to_jockey` varchar(50) DEFAULT NULL,
  `owner_name` varchar(10) DEFAULT NULL,
  `href_to_owner` varchar(50) DEFAULT NULL,
  `horse_weight` varchar(5) DEFAULT NULL,
  `horse_weight_increment` varchar(5) DEFAULT NULL,
  `win_odds` varchar(10) DEFAULT NULL,
  `popularity_order` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`race_id`,`horse_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;