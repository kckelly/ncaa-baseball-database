CREATE TABLE fielding_line
(
  game_id int NOT NULL REFERENCES game,
  roster_id int NOT NULL REFERENCES roster,
  tc int NOT NULL,
  po int NOT NULL,
  a int NOT NULL,
  e int NOT NULL,
  pb int NOT NULL,
  ci int NOT NULL,
  sb int NOT NULL,
  cs int NOT NULL,
  dp int NOT NULL,
  tp int NOT NULL,
  UNIQUE (game_id, roster_id)
);
