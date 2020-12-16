CREATE TABLE play_by_play
(
  game_id int NOT NULL REFERENCES game,
  team_id int NOT NULL REFERENCES team,
  inning int NOT NULL CHECK (inning > 0),
  side side NOT NULL,
  ord int NOT NULL,
  text text NOT NULL,
  pitches varchar,
  UNIQUE (game_id, team_id, inning, ord)
);
