CREATE TABLE school
(
  id SERIAL PRIMARY KEY,
  ncaa_id int UNIQUE,
  name varchar NOT NULL,
  nickname varchar NOT NULL,
  url varchar NOT NULL
);
