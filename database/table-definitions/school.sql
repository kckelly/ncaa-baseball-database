CREATE TABLE school
(
  id SERIAL PRIMARY KEY,
  ncaa_id int UNIQUE NOT NULL,
  name varchar NOT NULL,
  nickname varchar,
  url varchar
);
