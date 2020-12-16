CREATE TABLE year_info
(
  year int PRIMARY KEY,
  year_id int NOT NULL UNIQUE,
  hitting_id int UNIQUE NOT NULL,
  pitching_id int UNIQUE NOT NULL,
  fielding_id int UNIQUE NOT NULL
);
