CREATE TABLE game
(
  id SERIAL PRIMARY KEY,
  ncaa_id int UNIQUE,
  away_team_id int NOT NULL REFERENCES team,
  home_team_id int NOT NULL REFERENCES team,
  date date NOT NULL,
  location varchar,
  attendance int
);
