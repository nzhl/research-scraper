CREATE DATABASE IF NOT EXISTS research_scraper DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

USE research_scraper;

CREATE TABLE IF NOT EXISTS authors(
	id MEDIUMINT NOT NULL AUTO_INCREMENT, 

	# personally think 100 is big enough for a name.
	name VARCHAR(100) NOT NULL, 

	# https://dev.mysql.com/doc/refman/5.7/en/numeric-type-overview.html
	# only reigstered author can have account and password.
	is_registered BOOL NOT NULL DEFAULT FALSE,

	# tends to accept a email address.
	account VARCHAR(80),
	password VARCHAR(20),

       	# https://stackoverflow.com/questions/219569/best-database-field-type-for-a-url
	gs_link VARCHAR(2083),

	PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS authors_and_papers(
	author_id MEDIUMINT NOT NULL,
	paper_id MEDIUMINT NOT NULL,
	PRIMARY KEY(author_id, paper_id)
);

CREATE TABLE IF NOT EXISTS papers(
	id MEDIUMINT NOT NULL AUTO_INCREMENT, 

	# some articles get really long name.
	title VARCHAR(2000) NOT NULL,

	is_hidden BOOL NOT NULL DEFAULT FALSE,

	publication_date DATE,
	conference varchar(300),
	journal varchar(300),
	publisher varchar(300),
	total_citations MEDIUMINT,

	gs_link VARCHAR(2083),
	pdf_link varchar(2083),

	PRIMARY KEY(id)
);
