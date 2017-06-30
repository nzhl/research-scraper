create database if not exists unnc_scholar default character set utf8mb4 collate utf8mb4_general_ci;

use unnc_scholar;

create table if not exists authors(
	name varchar(100),
	tags varchar(300),
	url varchar(300)
);

create table if not exists articles(
	title varchar(500),
	authors varchar(500),
	publication_date varchar(300),
	conference varchar(300),
	journal varchar(300),
	publisher varchar(300),
	total_citations varchar(100),
	is_pdf varchar(100),
	url varchar(500)
);
