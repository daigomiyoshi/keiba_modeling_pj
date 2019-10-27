CREATE TABLE `keibalab_race_result_list` (
  `race_id` varchar(15) NOT NULL,
  `arrival_order` int NOT NULL,
  `post_position` int DEFAULT NULL,
  `horse_number` int DEFAULT NULL,
  `horse_name` varchar(50) DEFAULT NULL,
  `href_to_the_horse` varchar(100) DEFAULT NULL,
  `horse_age` varchar(10) DEFAULT NULL,
  `horse_weight` varchar(20) DEFAULT NULL,
  `horse_impost` float DEFAULT NULL,
  `jockey_name` varchar(50) DEFAULT NULL,
  `href_to_the_jockey` varchar(50) DEFAULT NULL,
  `popularity_order` int DEFAULT NULL,
  `win_odds` float DEFAULT NULL,
  `trainer_name` varchar(50) DEFAULT NULL,
  `href_to_the_trainer` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`race_id`, `arrival_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;