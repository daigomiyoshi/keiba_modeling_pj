CREATE TABLE `race_refund_info` (
  `race_id` varchar(15) NOT NULL,
  `refund_type` varchar(10) NOT NULL,
  `groupby_index` int(11) NOT NULL,
  `bracket_num` int(11) NOT NULL,
  `refund_yen` int(11) NOT NULL,
  `popularity_order` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;