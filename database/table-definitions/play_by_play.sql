CREATE TABLE play_by_play
(
  game_id int NOT NULL REFERENCES game,
  team_id int NOT NULL REFERENCES team,
  ord int NOT NULL,
  text text NOT NULL,
  UNIQUE (game_id, team_id, ord)
);
