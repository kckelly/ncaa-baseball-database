CREATE TABLE coach
(
  id SERIAL PRIMARY KEY,
  ncaa_id int UNIQUE,
  first_name varchar NOT NULL,
  last_name varchar NOT NULL,
  alma_mater varchar,
  year_graduated int
);
