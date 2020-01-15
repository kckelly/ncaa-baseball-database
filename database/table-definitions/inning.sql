CREATE TABLE inning
(
  game_id int NOT NULL REFERENCES game,
  team_id int NOT NULL REFERENCES team,
  inning int NOT NULL CHECK (inning > 0),
  runs int NOT NULL CHECK (runs >= 0),
  UNIQUE (game_id, team_id, inning)
);
