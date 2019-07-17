CREATE TABLE `keibalab_race_prior_info_list` (
  `race_id` varchar(15) NOT NULL DEFAULT '',
  `post_position` int(11) NOT NULL,
  `horse_number` int(11) NOT NULL,
  `horse_name` varchar(50) DEFAULT NULL,
  `href_to_the_horse` varchar(100) DEFAULT NULL,
  `jockey_name` varchar(50) DEFAULT NULL,
  `href_to_the_jockey` varchar(100) DEFAULT NULL,
  `trainer_name` varchar(50) DEFAULT NULL,
  `horse_age` varchar(10) DEFAULT NULL,
  `horse_sex` varchar(10) DEFAULT NULL,
  `popularity_order` int(11) DEFAULT NULL,
  `win_odds` float DEFAULT NULL,
  `horse_weight` varchar(20) DEFAULT NULL,
  `horse_weight_increment_from_previous` varchar(20) DEFAULT NULL,
  `owner_name` varchar(50) DEFAULT NULL,
  `href_to_the_owner` varchar(100) DEFAULT NULL,
  `breeder_name` varchar(50) DEFAULT NULL,
  `jockey_finish_first_second` varchar(50) DEFAULT NULL,
  `horse_number_finish_first_second` varchar(50) DEFAULT NULL,
  `stallion_finish_first_second` varchar(50) DEFAULT NULL,
  `conbi_finish_first_second` varchar(50) DEFAULT NULL,
  `zensou_info_list` text,
  PRIMARY KEY (`race_id`,`post_position`,`horse_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;