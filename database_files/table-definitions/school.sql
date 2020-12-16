CREATE TABLE school
(
  id SERIAL PRIMARY KEY,
  ncaa_id int UNIQUE,
  name varchar UNIQUE NOT NULL,
  nickname varchar,
  url varchar
);
