CREATE TYPE pos AS ENUM ('p', 'c', '1b', '2b', '3b', 'ss', 'lf', 'cf', 'rf', 'dh', 'ph', 'pr');

CREATE TABLE game_position
(
  game_id int NOT NULL REFERENCES game,
  roster_id int NOT NULL REFERENCES roster,
  position pos NOT NULL,
  UNIQUE (game_id, roster_id, position)
);
