CREATE DATABASE IF NOT EXISTS research_scraper DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

USE research_scraper;

DROP TABLE authors;
DROP TABLE papers;
DROP TABLE groups;
DROP TABLE authors_and_papers;
DROP TABLE authors_and_groups;

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
	last_update_date DATE,

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
	authors VARCHAR(2083) NOT NULL,

	is_hidden BOOL NOT NULL DEFAULT FALSE,

	publication_date DATE,
	conference varchar(300),
	journal varchar(300),
	publisher varchar(300),
	total_citations MEDIUMINT,

	gs_link VARCHAR(2083),
	pdf_link VARCHAR(2083),

	PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS authors_and_groups(
	author_id MEDIUMINT NOT NULL,
	group_id MEDIUMINT NOT NULL,
	PRIMARY KEY(author_id, group_id)
);

CREATE TABLE IF NOT EXISTS groups(
	id MEDIUMINT NOT NULL AUTO_INCREMENT,
	name VARCHAR(1000) NOT NULL,
	description VARCHAR(2000),
	group_link VARCHAR(2083),

	PRIMARY KEY(id)
);

/*

DELETE FROM authors;
DELETE FROM papers;
DELETE FROM groups;
DELETE FROM authors_and_papers;
DELETE FROM authors_and_groups;

INSERT INTO authors (name, is_registered,  account, password, gs_link) 
VALUES ('Author1', 1, 'a1', 'a1', 'https://www.google.co.uk');

INSERT INTO authors (name, is_registered,  account, password, gs_link) 
VALUES ('Author2', 1, 'a2', 'a2', 'https://www.google.co.uk');

INSERT INTO authors (name, is_registered,  account, password, gs_link) 
VALUES ('Author3', 1, 'a3', 'a3', 'https://www.google.co.uk');

INSERT INTO papers (title, gs_link, pdf_link)
VALUES ('p1', 'https://www.google.co.uk', '');

INSERT INTO papers (title, gs_link, pdf_link)
VALUES ('p2', '', 'https://www.google.co.uk');

INSERT INTO papers (title, gs_link, pdf_link)
VALUES ('p3', 'https://www.google.co.uk', 'https://www.google.co.uk');

INSERT INTO papers (title, gs_link, pdf_link)
VALUES ('p4', 'https://www.google.co.uk', 'https://www.google.co.uk');

INSERT INTO papers (title, gs_link, pdf_link)
VALUES ('p5', 'https://www.google.co.uk', '');

INSERT INTO papers (title, gs_link, pdf_link)
VALUES ('p6', '', 'https://www.google.co.uk');

INSERT INTO groups (name) VALUES ('g1');
INSERT INTO groups (name) VALUES ('g2');

INSERT INTO authors_and_papers VALUES (1, 1);
INSERT INTO authors_and_papers VALUES (1, 2);
INSERT INTO authors_and_papers VALUES (1, 4);

INSERT INTO authors_and_papers VALUES (2, 3);
INSERT INTO authors_and_papers VALUES (2, 6);

INSERT INTO authors_and_papers VALUES (3, 4);
INSERT INTO authors_and_papers VALUES (3, 5);
INSERT INTO authors_and_papers VALUES (3, 6);

INSERT INTO authors_and_groups VALUES (1, 1);

INSERT INTO authors_and_groups VALUES (2, 1);
INSERT INTO authors_and_groups VALUES (2, 2);

INSERT INTO authors_and_groups VALUES (3, 2);
*/

