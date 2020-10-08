CREATE TABLE player
(
  id SERIAL PRIMARY KEY,
  ncaa_id int NULL UNIQUE,
  first_name varchar NOT NULL,
  last_name varchar NOT NULL
);
