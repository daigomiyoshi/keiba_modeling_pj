CREATE TABLE `race_master_not_existing` (
  `race_id` varchar(15) NOT NULL,
  PRIMARY KEY (`race_id`),
  KEY `race_id` (`race_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;