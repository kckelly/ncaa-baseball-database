CREATE TABLE conference
(
  id SERIAL PRIMARY KEY,
  name varchar NOT NULL,
  division int CHECK (division = 1 OR division = 2 OR division = 3),
  UNIQUE (name, division)
);
