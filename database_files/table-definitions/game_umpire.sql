CREATE TABLE game_umpire
(
  game_id int NOT NULL REFERENCES game,
  umpire_id int NOT NULL REFERENCES umpire,
  position ump_pos NOT NULL,
  --UNIQUE (game_id, umpire_id),
  UNIQUE (game_id, position)
);
