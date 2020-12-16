CREATE TABLE game_position
(
  game_id int NOT NULL REFERENCES game,
  roster_id int NOT NULL REFERENCES roster,
  ord int,
  position pos NOT NULL,
  UNIQUE (game_id, roster_id, position)
);
