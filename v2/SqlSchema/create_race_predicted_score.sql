CREATE TABLE `race_predicted_score` (
  `race_id` varchar(15) NOT NULL,
  `horse_num` int(11) NOT NULL,
  `predicted_score` float DEFAULT NULL,
  PRIMARY KEY (`race_id`,`horse_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

